# Readiness Probe

A readiness probe tells Kubernetes whether a container is ready to receive traffic. When the readiness probe fails, Kubernetes removes the pod from service endpoints even if the container is still running.

This is different from a liveness probe. A liveness probe checks whether the container is alive. If the liveness probe fails, Kubernetes restarts the container. A readiness probe does not restart the container; it simply marks the pod as not ready.

## Why readiness matters

Readiness is important for rolling updates, load balancing, and zero-downtime deployments. A pod that is still starting up or still warming caches should not receive user traffic.

For example, an application may take several seconds to initialize a database connection. During that time, the readiness probe can fail. Once initialization finishes and the probe passes, the pod is added back to the service endpoints.

## Typical readiness probe types

Kubernetes supports several probe types:

- HTTP GET: sends an HTTP request to a path and expects a success status code
- TCP socket: checks whether a port is open
- Exec: runs a command inside the container and checks exit status

## Example

```yaml
readinessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

In this example, Kubernetes waits 5 seconds after startup, then probes the `/healthz` endpoint every 10 seconds. If it fails 3 times in a row, the pod is marked not ready.

## Readiness vs startup probe

A startup probe is used to tell Kubernetes whether the application has finished its initial startup. It can be more tolerant during slow startup and prevents liveness failures from restarting a still-initializing container.

- Readiness: is this pod ready to serve traffic?
- Liveness: is this container still alive?
- Startup: has application startup completed?

## Production guidance

Use readiness probes to control traffic routing. Use startup probes for slow-start applications to avoid false restarts. Use liveness probes carefully because they can cause restarts during transient issues.

A common pattern is:

- startup probe: long timeout, slower thresholds
- readiness probe: health check for actual service readiness
- liveness probe: simple check to catch deadlocked or hung processes

## Summary

Readiness probes let Kubernetes route traffic only to healthy pods. They are critical in production for graceful rolling upgrades and reliable load balancing.
