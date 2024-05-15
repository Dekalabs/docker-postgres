import re
import time
from typing import TYPE_CHECKING
import docker
import os

import pytest

if TYPE_CHECKING:
    from docker.models.containers import Container
    from docker.models.images import Image

client = docker.from_env()
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backup_pattern = r"backup_\d{4}_\d{2}_\d{2}T\d{2}_\d{2}_\d{2}\.sql\.gz"
versions = ["10", "11", "12", "13", "14"]
default_retries = 3


@pytest.fixture(autouse=True)
def cleanup_backups_and_containers():
    yield
    print("Cleaning up backups and containers...")
    for root, _, files in os.walk(os.path.join(base_path, "tests")):
        for file in files:
            if re.match(backup_pattern, file):
                os.remove(os.path.join(root, file))
    print(client.containers.list(all=True))
    for container in client.containers.list(all=True):
        if "test_postgres" in container.name:
            container.stop()
            container.remove()


@pytest.fixture(scope="module", autouse=True)
def cleanup_images():
    yield
    # This should run after all containers are stopped and removed.
    print("Cleaning up images...")
    for image in client.images.list():
        if any(tag.startswith("test_postgres") for tag in image.tags):
            client.images.remove(image.id, force=True)


def get_or_build_image(version: str):
    for image in client.images.list():
        if any(tag.startswith(f"test_postgres_{version}") for tag in image.tags):
            print(f"Using existing PostgreSQL {version} image...")
            return image
    dockerfile_path = os.path.join(base_path, "postgres", version, "Dockerfile")
    print(f"Building PostgreSQL {version} image...")
    image, build_logs = client.images.build(
        path=base_path, dockerfile=dockerfile_path, tag=f"test_postgres_{version}"
    )
    for log in build_logs:
        if "stream" in log:
            print(log["stream"], end="")
    return image


def run_container(image: "Image", **kwargs):
    opts = {
        "name": image.tags[0].split(":")[0],
        "detach": True,
        "ports": {"5432/tcp": 5432},
        "environment": {
            "POSTGRES_USER": "user",
            "POSTGRES_PASSWORD": "password",
            "POSTGRES_DB": "app",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
        },
        "volumes": {
            os.path.join(base_path, "tests"): {"bind": "/backups", "mode": "rw"}
        },
    } | kwargs
    return client.containers.run(image.id, **opts)


def wait_until_pg_isready(container: "Container"):
    retries = default_retries
    while retries > 0:
        out = container.exec_run("pg_isready")
        if out.exit_code == 0:
            break
        retries -= 1
        time.sleep(1)


@pytest.mark.parametrize(["version"], [[version] for version in versions])
def test_backup(version: str):
    """Test that the backup command creates a backup file."""
    image = get_or_build_image(version)
    container = run_container(image)
    wait_until_pg_isready(container)
    out = container.exec_run("backup")
    assert out.exit_code == 0
    backup_file_match = re.search(backup_pattern, out.output.decode("utf-8"))
    assert backup_file_match


@pytest.mark.parametrize(["version"], [[version] for version in versions])
def test_backups(version: str):
    """Test that the backups command lists the backup files."""
    image = get_or_build_image(version)
    container = run_container(image)
    wait_until_pg_isready(container)
    out = container.exec_run("backup")
    assert out.exit_code == 0
    backup_file_match = re.search(backup_pattern, out.output.decode("utf-8"))
    assert backup_file_match
    backup_file = backup_file_match.group()
    out = container.exec_run("backups")
    assert out.exit_code == 0
    assert backup_file in out.output.decode("utf-8")


@pytest.mark.parametrize(["version"], [[version] for version in versions])
def test_restore(version: str):
    """Test that the restore command restores the state of a backup file."""
    image = get_or_build_image(version)
    container = run_container(image)
    wait_until_pg_isready(container)
    # Create a table and insert a row.
    out = container.exec_run(
        "psql -U user -d app -c 'CREATE TABLE companies (name text);'"
    )
    assert out.exit_code == 0
    out = container.exec_run(
        "psql -U user -d app -c \"INSERT INTO companies VALUES ('dekalabs');\""
    )
    assert out.exit_code == 0
    # Backup the database.
    out = container.exec_run("backup")
    assert out.exit_code == 0
    backup_file_match = re.search(backup_pattern, out.output.decode("utf-8"))
    assert backup_file_match
    backup_file = backup_file_match.group()
    # Drop the table and check that it doesn't exist.
    container.exec_run("psql -U user -d app -c 'DROP TABLE companies;'")
    out = container.exec_run("psql -U user -d app -c 'SELECT * FROM companies;'")
    assert out.exit_code != 0
    # Restore the database and check that the table exists.
    out = container.exec_run(f"restore {backup_file}")
    assert out.exit_code == 0
    out = container.exec_run("psql -U user -d app -c 'SELECT * FROM companies;'")
    assert out.exit_code == 0
    assert "dekalabs" in out.output.decode("utf-8")


@pytest.mark.parametrize(["version"], [[version] for version in versions])
def test_createreaduser(version: str):
    """Test that the createreaduser command creates a read-only user."""
    image = get_or_build_image(version)
    container = run_container(
        image,
        environment={
            "POSTGRES_USER": "user",
            "POSTGRES_PASSWORD": "password",
            "POSTGRES_DB": "app",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_READ_ONLY_USER": "readuser",
            "POSTGRES_READ_ONLY_PASSWORD": "readpassword",
        },
    )
    wait_until_pg_isready(container)
    # Create a table and insert a row.
    out = container.exec_run(
        "psql -U user -d app -c 'CREATE TABLE companies (name text);'"
    )
    assert out.exit_code == 0
    # Create a read-only user.
    out = container.exec_run("createreaduser")
    assert out.exit_code == 0
    # Check that the read-only user can read the table but not write.
    out = container.exec_run("psql -U readuser -d app -c 'SELECT * FROM companies;'")
    assert out.exit_code == 0
    out = container.exec_run(
        "psql -U readuser -d app -c 'CREATE TABLE employees (name text);'"
    )
    assert out.exit_code != 0
    out = container.exec_run(
        "psql -U readuser -d app -c \"INSERT INTO companies VALUES ('dekalabs');\""
    )
    assert out.exit_code != 0
