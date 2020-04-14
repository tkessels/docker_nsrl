FROM alpine

MAINTAINER tabledevil

COPY nsrl /nsrl
RUN apk add -U tini gcc libc-dev python-dev py-pip p7zip python \
  && pip install pybloom \
  && /nsrl/shrink_nsrl.sh \
  && apk del --purge gcc libc-dev python-dev py-pip p7zip \
  && rm -rf /tmp/* /root/.cache /var/cache/apk/* /nsrl/shrink_nsrl.sh

WORKDIR /nsrl

ENTRYPOINT ["/sbin/tini","--","/nsrl/search.py"]

CMD ["-h"]
