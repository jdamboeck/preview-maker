FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set up locale
RUN apt-get update && apt-get install -y locales && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install GTK 4.0 and dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools \
    python3-wheel \
    # Pre-installed GTK and GObject packages
    python3-gi \
    python3-gi-cairo \
    python3-cairo \
    # System dependencies
    libgtk-4-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-4.0 \
    python3-cairo-dev \
    libglib2.0-dev \
    # Additional dependencies for GObject Introspection
    gobject-introspection \
    gir1.2-glib-2.0 \
    # Xvfb for headless testing
    xvfb \
    # Utilities
    git \
    vim \
    nano \
    sudo \
    # Tools for debugging
    gdb \
    strace \
    ltrace \
    valgrind \
    heaptrack \
    python3-ipdb \
    # Add CI/Testing tools
    python3-pytest \
    python3-pytest-cov \
    # X11 utilities for GUI testing
    x11-utils \
    x11-apps \
    mesa-utils \
    # Add system monitoring tools
    htop \
    iotop \
    psmisc \
    # Add network tools for API debugging
    curl \
    wget \
    jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up non-root user
RUN useradd -ms /bin/bash developer
RUN usermod -aG sudo developer
RUN echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up Python environment
WORKDIR /home/developer
USER developer

# Create Python virtual environment with system site packages to access PyGObject
RUN python3 -m venv /home/developer/.venv --system-site-packages
ENV PATH="/home/developer/.venv/bin:$PATH"
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Install Python packages (excluding PyGObject and related packages which we use from system)
COPY --chown=developer:developer docker/requirements.txt /tmp/
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# Set up X11 forwarding
ENV DISPLAY=:0

# Create directory structure for the application
RUN mkdir -p /home/developer/app/components/ui \
    /home/developer/app/utils \
    /home/developer/tests \
    /home/developer/resources

# Copy entrypoint script
COPY --chown=developer:developer docker/entrypoint.sh /home/developer/entrypoint.sh
RUN chmod +x /home/developer/entrypoint.sh

# Working directory
WORKDIR /app

# Entrypoint
ENTRYPOINT ["/home/developer/entrypoint.sh"]
CMD ["bash"]