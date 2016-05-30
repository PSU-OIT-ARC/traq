############################
#                          #
#  Oregon Registry Online  #
#  Ubuntu Docker Image     #
#                          #
############################
FROM psuarc/web:python3
MAINTAINER Thom Linton <tlinton@pdx.edu>
VOLUME /opt/host/

# Add docker assets to container
COPY /assets /usr/local/docker/
COPY /bin /usr/local/docker/bin

# Install repositories, dependencies and update system packages
RUN /usr/local/docker/bin/install_dependencies.sh

# System property configuration
RUN /usr/local/docker/bin/configure_system.sh

# Entry-point configuration
COPY entrypoint.sh /usr/local/docker/
ENTRYPOINT ["/usr/local/docker/entrypoint.sh"]
