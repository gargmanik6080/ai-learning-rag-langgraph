# Pod Lifecycle

A pod is the smallest deployable unit in Kubernetes. It can contain one or more containers and moves through a defined lifecycle from creation to termination.

## Pod phases

Kubernetes tracks a pod's lifecycle with phases:

- Pending: the pod has been accepted by the cluster but is not running yet
- Running: at least one container is running and the pod is healthy enough to execute work
- Succeeded: all containers terminated successfully and the pod will not restart
- Failed: one or more containers terminated and at least one failed
- Unknown: the state cannot be determined

## Common lifecycle states

A pod can also have container-level states:

- Waiting: the container is stuck waiting for something like image pull or network setup
- Running: the container is actively executing
- Terminated: the container ended normally or crashed

## Typical sequence

A pod usually progresses in this order:

1. Kubernetes schedules the pod to a node
2. The kubelet pulls the container image
3. The container starts
4. The kubelet runs liveness, readiness, and startup checks
5. The pod becomes Ready when readiness checks pass
6. The pod receives traffic or runs workloads
7. The pod is terminated during a rollout, node shutdown, or manual delete

## CrashLoopBackOff

A CrashLoopBackOff state happens when a container repeatedly crashes and restarts. This usually means the application exits immediately, often due to configuration errors, invalid command arguments, missing dependencies, or a failing health check.

## Example lifecycle flow

```text
Pending
  -> Running
      -> Ready
      -> Restarting (if liveness fails)
      -> Failed or Terminated
```

## Container restart behavior

If a container exits unexpectedly, Kubernetes may restart it according to the pod restart policy. By default, restartPolicy is Always for pods with containers that should be continuously running.

## Why the lifecycle matters

Understanding pod lifecycle is critical for debugging Kubernetes workloads. If a pod is stuck in Pending, the issue may be scheduling, image pull, or resource constraints. If it is Running but not Ready, the issue may be readiness probe failures. If it is CrashLoopBackOff, the problem is usually in the container startup path or app configuration.

## Summary

The pod lifecycle is the operational heartbeat of Kubernetes. Observing pod phase and container state helps engineers diagnose everything from image pull issues to misconfigured probes and failed application startup.
