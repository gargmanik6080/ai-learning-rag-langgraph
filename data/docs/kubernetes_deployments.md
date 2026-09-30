# Kubernetes Deployments

A Deployment is a Kubernetes object used to manage stateless application workloads. It ensures that a desired number of replicas are running and updates them in a controlled, rolling manner.

## What a Deployment does

The Deployment controller watches the desired state specified in the manifest and reconciles the live state. If a pod disappears, the controller creates a replacement. If a new version of the application is rolled out, it creates new pods gradually and removes old ones only when the new ones are ready.

## Common fields

A standard Deployment includes:

- `apiVersion`: Kubernetes API version
- `kind`: Deployment
- `metadata`: name, namespace, labels
- `spec.replicas`: desired number of pod replicas
- `selector`: label selector used to match pods
- `template`: pod template used to create new pods
- `strategy`: update strategy, often `RollingUpdate`

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
```

## Rolling update behavior

Deployments use a rolling update strategy by default. Kubernetes creates new pods with the new version while keeping old ones available until the new pods are healthy. This reduces downtime and makes deployment safer.

A rolling update can be controlled with:

- `maxUnavailable`: how many pods can be unavailable during the rollout
- `maxSurge`: how many extra pods can be created above the desired replica count

## Why Deployment is useful

Deployments are ideal for stateless services such as APIs, web apps, workers, and other systems that can be replicated horizontally. They allow:

- declarative configuration
- self-healing behavior
- versioned rollouts
- easy scaling

## Deployment vs StatefulSet

A Deployment manages stateless workloads and does not guarantee stable pod identities. A StatefulSet is better for stateful workloads such as databases, where each pod has stable network identity and persistent storage.

## Deployment vs DaemonSet

A DaemonSet ensures that a copy of a pod runs on every node or selected nodes. A Deployment typically spreads replicas across the cluster. Use DaemonSet for node-level agents or monitoring daemons.

## Troubleshooting tips

If a Deployment is not progressing, common causes include:

- no available nodes for scheduling
- image pull failures
- readiness probes failing
- resource constraints or quota limits

You can inspect Deployment status with:

```bash
kubectl get deployment
kubectl describe deployment <name>
kubectl rollout status deployment/<name>
```

## Summary

Deployments are the standard way to run stateless applications in Kubernetes. They provide a clean declarative interface for scaling, self-healing, and controlled rollout updates.
