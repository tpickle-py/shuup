FROM node:18-bookworm-slim as base

# This image is NOT made for production use.
LABEL maintainer="Shuup Commerce Inc. <support@shuup.com>"

RUN apt-get update \
    && apt-get --assume-yes install \
    curl \
    libpangocairo-1.0-0 \
    python3 \
    python3-dev \
    python3-pil \
    python3-pip \
    && rm -rf /var/lib/apt/lists/ /var/cache/apt/

# Install uv for faster package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# These invalidate the cache every single time but
# there really isn't any other obvious way to do this.
COPY . /app
WORKDIR /app

# The dev compose file sets this to 1 to support development and editing the source code.
# The default value of 0 just installs the demo for running.
ARG editable=0

RUN if [ "$editable" -eq 1 ]; then \
    uv sync && \
    uv run shuup-build-resources; \
    else \
    pip3 install shuup; \
    fi

RUN if [ "$editable" -eq 1 ]; then \
    uv run shuup_workbench migrate --settings=shuup_workbench.settings.dev; \
    else \
    python3 -m shuup_workbench migrate; \
    fi

RUN if [ "$editable" -eq 1 ]; then \
    uv run shuup_workbench shuup_init --settings=shuup_workbench.settings.dev; \
    else \
    python3 -m shuup_workbench shuup_init; \
    fi

RUN echo '\
    from django.contrib.auth import get_user_model\n\
    from django.db import IntegrityError\n\
    try:\n\
    get_user_model().objects.create_superuser("admin", "admin@admin.com", "admin")\n\
    except IntegrityError:\n\
    pass\n' | \
    if [ "$editable" -eq 1 ]; then \
    uv run shuup_workbench shell --settings=shuup_workbench.settings.dev; \
    else \
    python3 -m shuup_workbench shell; \
    fi

CMD if [ -f "pyproject.toml" ]; then \
    uv run shuup_workbench runserver 0.0.0.0:8000 --settings=shuup_workbench.settings.dev; \
    else \
    python3 -m shuup_workbench runserver 0.0.0.0:8000; \
    fi
