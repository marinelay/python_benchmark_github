FROM marinelay/pypebugs:base

ARG USERNAME=wonseok
ARG PROJECT
ARG VERSION

# make directory
USER root
RUN mkdir /pyfix_bench && chmod 777 /pyfix_bench
USER ${USERNAME}
WORKDIR /pyfix_bench

# copy file
COPY benchmark/${PROJECT}/${PROJECT}-${VERSION}/bug_info.json /pyfix_bench/bug_info.json
COPY setup.sh /pyfix_bench/setup.sh

USER root
RUN chmod +x setup.sh
USER ${USERNAME}
RUN ./setup.sh

