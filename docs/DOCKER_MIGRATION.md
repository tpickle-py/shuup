# Docker Migration Guide

## Updated Docker Setup

The Shuup project now includes modern Docker configurations optimized for the new uv-based development workflow.

## Available Docker Configurations

### 1. **Dockerfile.uv** (Recommended)
- Uses the official uv Docker image for faster builds
- Optimized layer caching with uv's dependency resolution
- Modern Python 3.11 base

### 2. **Dockerfile** (Legacy Compatible)
- Updated to support both uv and traditional pip workflows
- Backward compatible with existing setups
- Uses conditional logic to detect development mode

## Docker Compose Files

### docker-compose.uv.yml (Recommended)
```bash
docker-compose -f docker-compose.uv.yml up
```
- Uses Dockerfile.uv for fastest setup
- Includes health checks
- Optional PostgreSQL service

### docker-compose-dev.yml (Development)
```bash
docker-compose -f docker-compose-dev.yml up
```
- Development mode with volume mounting
- Live code reloading
- Excludes virtual environment from sync

### docker-compose.yml (Legacy)
```bash
docker-compose up
```
- Traditional setup for backward compatibility

## Migration Steps

1. **For new projects**: Use `docker-compose.uv.yml`
2. **For existing projects**: Gradually migrate to `docker-compose-dev.yml` then `docker-compose.uv.yml`
3. **For CI/CD**: Update your pipelines to use the new Dockerfile.uv

## Benefits

- **Faster builds**: uv is significantly faster than pip
- **Better caching**: Optimized Docker layer structure
- **Modern base**: Python 3.11 with latest security updates
- **Smaller images**: More efficient dependency resolution
