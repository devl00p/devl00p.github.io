---
title: "Solution du challenge Buenos Aires de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Buenos Aires": Kubernetes Pod Crashing

**Level:** Medium

**Type:** Fix

**Tags:** [kubernetes](https://sadservers.com/tag/kubernetes)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** There are two brothers (pods) logger and logshipper living in the default namespace. Unfortunately, logshipper has an issue (crashlooping) and is forbidden to see what logger is trying to say. Could you help fix Logshipper? You can check the status of the pods with kubectl get pods

Do not change the K8S definition of the logshipper pod. Use "sudo".

Credit [Srivatsav Kondragunta](https://www.linkedin.com/in/srivatsav-kondragunta/)

**Test:** `kubectl get pods -l app=logshipper --no-headers -o json | jq -r '.items[] | "\(.status.containerStatuses[0].state.waiting.reason // .status.phase)"'` returns _Running_

**Time to Solve:** 20 minutes.

Jetons d'abord un œil à l'état des pods.

```console
admin@i-0e4e27bcd80b580d8:~$ kubectl get pods
WARN[0000] Unable to read /etc/rancher/k3s/k3s.yaml, please start server with --write-kubeconfig-mode to modify kube config permissions 
error: error loading config file "/etc/rancher/k3s/k3s.yaml": open /etc/rancher/k3s/k3s.yaml: permission denied
admin@i-0e4e27bcd80b580d8:~$ sudo kubectl get pods
NAME                         READY   STATUS             RESTARTS       AGE
logger-574bd75fd9-wpg4w      1/1     Running            5 (36s ago)    134d
logshipper-7d97c8659-npscd   0/1     CrashLoopBackOff   21 (13s ago)   134d
```

Pourquoi le second pod est-il en carafe ?

```console
admin@i-0e4e27bcd80b580d8:~$ sudo kubectl describe pod logshipper-7d97c8659-npscd
Name:             logshipper-7d97c8659-npscd
Namespace:        default
Priority:         0
Service Account:  logshipper-sa
Node:             node1/172.31.35.204
Start Time:       Mon, 23 Oct 2023 02:50:49 +0000
Labels:           app=logshipper
                  pod-template-hash=7d97c8659
Annotations:      kubectl.kubernetes.io/restartedAt: 2023-10-23T02:50:49Z
Status:           Running
IP:               10.42.1.41
IPs:
  IP:           10.42.1.41
Controlled By:  ReplicaSet/logshipper-7d97c8659
Containers:
  logshipper:
    Container ID:  containerd://1f33227c86f391f5b5d79457d18d05860a65dc8dbadeb2fc9a3a91832e6afa0d
    Image:         logshipper:v3
    Image ID:      sha256:d61303b070c3fc3d05bf70e8ef848881183480bee823b436ecb7c303e89e4010
    Port:          <none>
    Host Port:     <none>
    Command:
      /usr/bin/python3
      logshipper.py
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
      Started:      Tue, 05 Mar 2024 12:38:53 +0000
      Finished:     Tue, 05 Mar 2024 12:38:54 +0000
    Ready:          False
    Restart Count:  22
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-2xdwr (ro)
Conditions:
  Type              Status
  Initialized       True 
  Ready             False 
  ContainersReady   False 
  PodScheduled      True 
Volumes:
  kube-api-access-2xdwr:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason          Age                   From               Message
  ----     ------          ----                  ----               -------
  Normal   Scheduled       134d                  default-scheduler  Successfully assigned default/logshipper-7d97c8659-npscd to node1
  Normal   Pulled          134d (x4 over 134d)   kubelet            Container image "logshipper:v3" already present on machine
  Normal   Created         134d (x4 over 134d)   kubelet            Created container logshipper
  Normal   Started         134d (x4 over 134d)   kubelet            Started container logshipper
  Warning  BackOff         134d (x4 over 134d)   kubelet            Back-off restarting failed container logshipper in pod logshipper-7d97c8659-npscd_default(78da0880-1dc1-4ea8-a28b-8e393225a8ff)
  Normal   SandboxChanged  134d                  kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal   Created         134d (x4 over 134d)   kubelet            Created container logshipper
  Normal   Started         134d (x4 over 134d)   kubelet            Started container logshipper
  Warning  BackOff         134d (x12 over 134d)  kubelet            Back-off restarting failed container logshipper in pod logshipper-7d97c8659-npscd_default(78da0880-1dc1-4ea8-a28b-8e393225a8ff)
  Normal   Pulled          134d (x5 over 134d)   kubelet            Container image "logshipper:v3" already present on machine
  Normal   SandboxChanged  134d                  kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal   Pulled          134d (x3 over 134d)   kubelet            Container image "logshipper:v3" already present on machine
  Normal   Created         134d (x3 over 134d)   kubelet            Created container logshipper
  Normal   Started         134d (x3 over 134d)   kubelet            Started container logshipper
  Warning  BackOff         134d (x4 over 134d)   kubelet            Back-off restarting failed container logshipper in pod logshipper-7d97c8659-npscd_default(78da0880-1dc1-4ea8-a28b-8e393225a8ff)
  Normal   SandboxChanged  134d                  kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal   Pulled          134d (x4 over 134d)   kubelet            Container image "logshipper:v3" already present on machine
  Normal   Created         134d (x4 over 134d)   kubelet            Created container logshipper
  Normal   Started         134d (x4 over 134d)   kubelet            Started container logshipper
  Warning  BackOff         134d (x12 over 134d)  kubelet            Back-off restarting failed container logshipper in pod logshipper-7d97c8659-npscd_default(78da0880-1dc1-4ea8-a28b-8e393225a8ff)
  Normal   SandboxChanged  134d                  kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal   Pulled          134d (x2 over 134d)   kubelet            Container image "logshipper:v3" already present on machine
  Normal   Created         134d (x2 over 134d)   kubelet            Created container logshipper
  Normal   Started         134d (x2 over 134d)   kubelet            Started container logshipper
  Warning  BackOff         134d (x3 over 134d)   kubelet            Back-off restarting failed container logshipper in pod logshipper-7d97c8659-npscd_default(78da0880-1dc1-4ea8-a28b-8e393225a8ff)
  Normal   SandboxChanged  76s                   kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal   Pulled          32s (x3 over 74s)     kubelet            Container image "logshipper:v3" already present on machine
  Normal   Created         32s (x3 over 74s)     kubelet            Created container logshipper
  Normal   Started         32s (x3 over 73s)     kubelet            Started container logshipper
  Warning  BackOff         3s (x7 over 70s)      kubelet            Back-off restarting failed container logshipper in pod logshipper-7d97c8659-npscd_default(78da0880-1dc1-4ea8-a28b-8e393225a8ff)
```

On en sait pas plus, on va regarder les logs :

```console
admin@i-0e4e27bcd80b580d8:~$ sudo kubectl logs logshipper-7d97c8659-npscd
Exception when calling CoreV1Api->read_namespaced_pod_log: (403)
Reason: Forbidden
HTTP response headers: HTTPHeaderDict({'Audit-Id': '04703e59-e866-44f2-b339-cbb5ecad1a1b', 'Cache-Control': 'no-cache, private', 'Content-Type': 'application/json', 'X-Content-Type-Options': 'nosniff', 'Date': 'Tue, 05 Mar 2024 12:39:38 GMT', 'Content-Length': '352'})
HTTP response body: {"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"pods \"logger-574bd75fd9-wpg4w\" is forbidden: User \"system:serviceaccount:default:logshipper-sa\" cannot get resource \"pods/log\" in API group \"\" in the namespace \"default\"","reason":"Forbidden","details":{"name":"logger-574bd75fd9-wpg4w","kind":"pods"},"code":403}
```

Le pod est associé à un compte `system:serviceaccount:default:logshipper-sa`.

Il y a une tentative d'utiliser l'endpoint `pods/log` de l'API docker, mais le compte ne dispose pas de ces permissions.

Sur le pod qui fonctionne correctement, il n'y a rien d'intéressant :

```console
admin@i-0e4e27bcd80b580d8:~$ sudo kubectl describe pod logger-574bd75fd9-wpg4w
Name:             logger-574bd75fd9-wpg4w
Namespace:        default
Priority:         0
Service Account:  default
Node:             node1/172.31.35.204
Start Time:       Mon, 23 Oct 2023 02:40:44 +0000
Labels:           app=logger
                  pod-template-hash=574bd75fd9
Annotations:      <none>
Status:           Running
IP:               10.42.1.38
IPs:
  IP:           10.42.1.38
Controlled By:  ReplicaSet/logger-574bd75fd9
Containers:
  logger:
    Container ID:  containerd://1a999268ee5aa3c21392f53585ac2e6d3a9e976e6054f0ba6addf4ae9e0dd174
    Image:         busybox
    Image ID:      sha256:a416a98b71e224a31ee99cff8e16063554498227d2b696152a9c3e0aa65e5824
    Port:          <none>
    Host Port:     <none>
    Command:
      /bin/sh
      -c
      --
    Args:
      while true; do sleep 1; echo 'Hi, My brother logshipper cannot see what I am saying. Can you fix him?' ; done;
    State:          Running
      Started:      Tue, 05 Mar 2024 12:38:11 +0000
    Last State:     Terminated
      Reason:       Unknown
      Exit Code:    255
      Started:      Mon, 23 Oct 2023 04:25:25 +0000
      Finished:     Tue, 05 Mar 2024 12:38:06 +0000
    Ready:          True
    Restart Count:  5
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-s7cj9 (ro)
Conditions:
  Type              Status
  Initialized       True 
  Ready             True 
  ContainersReady   True 
  PodScheduled      True 
Volumes:
  kube-api-access-s7cj9:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason          Age    From               Message
  ----    ------          ----   ----               -------
  Normal  Scheduled       134d   default-scheduler  Successfully assigned default/logger-574bd75fd9-wpg4w to node1
  Normal  Pulled          134d   kubelet            Container image "busybox" already present on machine
  Normal  Created         134d   kubelet            Created container logger
  Normal  Started         134d   kubelet            Started container logger
  Normal  SandboxChanged  134d   kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal  Pulled          134d   kubelet            Container image "busybox" already present on machine
  Normal  Created         134d   kubelet            Created container logger
  Normal  Started         134d   kubelet            Started container logger
  Normal  SandboxChanged  134d   kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal  Pulled          134d   kubelet            Container image "busybox" already present on machine
  Normal  Created         134d   kubelet            Created container logger
  Normal  Started         134d   kubelet            Started container logger
  Normal  SandboxChanged  134d   kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal  Pulled          134d   kubelet            Container image "busybox" already present on machine
  Normal  Created         134d   kubelet            Created container logger
  Normal  Started         134d   kubelet            Started container logger
  Normal  SandboxChanged  134d   kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal  Pulled          134d   kubelet            Container image "busybox" already present on machine
  Normal  Created         134d   kubelet            Created container logger
  Normal  Started         134d   kubelet            Started container logger
  Normal  SandboxChanged  4m47s  kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal  Pulled          4m45s  kubelet            Container image "busybox" already present on machine
  Normal  Created         4m45s  kubelet            Created container logger
  Normal  Started         4m44s  kubelet            Started container logger
```

Quand on regarde le script `check.sh` on voit que le pod en souffrance doit passer en état _Running_, mais aussi que le service account doit rester le même.

```console
#!/usr/bin/bash
res=$(sudo kubectl get pods -l app=logshipper --no-headers -o json | jq -r '.items[] | "\(.status.containerStatuses[0].state.waiting.reason // .status.phase)"')
res=$(echo $res|tr -d '\r')

if [[ "$res" != "Running" ]]
then
  echo -n "NO"
  exit
fi


res=$(sudo k3s kubectl get pods -l app=logshipper --no-headers -o custom-columns=":.spec.serviceAccountName")
res=$(echo $res|tr -d '\r')

if [[ "$res" = "logshipper-sa" ]]
then
  echo -n "OK"
else
  echo -n "NO"
fi
```

J'ai demandé de l'aide à ChatGPT car je ne maitrise pas la notion de rôles sur _kubectl_.

```console
admin@i-0c80009b8691b12c8:~$ sudo kubectl get rolebindings,clusterrolebindings --all-namespaces -o custom-columns='KIND:kind,NAMESPACE:metadata.namespace,NAME:metadata.name,SERVICE_ACCOUNT:subjects[?(@.kind=="ServiceAccount")].name,ROLE:roleRef.name,CLUSTER_ROLE:roleRef.name' | grep logshipper
ClusterRoleBinding   <none>        logshipper-cluster-role-binding                        logshipper-sa                            logshipper-cluster-role                                logshipper-cluster-role
```

Le compte est lié à un "role-binding" (sorte de jointure) nommé `logshipper-cluster-role-binding` lui-même lié au rôle `logshipper-cluster-role` :

```console
admin@i-0c80009b8691b12c8:~$ sudo kubectl describe clusterrolebinding logshipper-cluster-role-binding
Name:         logshipper-cluster-role-binding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  logshipper-cluster-role
Subjects:
  Kind            Name           Namespace
  ----            ----           ---------
  ServiceAccount  logshipper-sa  default
```

L'idée est de rajouter un rôle permettant la consultation des logs que l'on rattachera via un binding au compte du pod.

Pour cela, il faut créer deux fichiers de déclaration, le premier pour le rôle, le second pour le binding :

```console
admin@i-0c80009b8691b12c8:~$ cat log-reader-role.yaml 
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: log-reader-role
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get", "list"]

admin@i-0c80009b8691b12c8:~$ cat log-reader-role-binding.yaml 
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: log-reader-role-binding
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: log-reader-role  # Use the name of the Role or ClusterRole you created
subjects:
- kind: ServiceAccount
  name: logshipper-sa
  namespace: default

admin@i-0c80009b8691b12c8:~$ sudo kubectl apply -f log-reader-role.yaml
role.rbac.authorization.k8s.io/log-reader-role created
admin@i-0c80009b8691b12c8:~$ sudo kubectl apply -f log-reader-role-binding.yaml
rolebinding.rbac.authorization.k8s.io/log-reader-role-binding created
```

Une fois qu'ils ont été appliqués avec `kubectl apply` il faut compter 5 minutes avant que les modifications soient prises en compte :

```console
admin@i-0c80009b8691b12c8:~$ sudo kubectl get pods
NAME                         READY   STATUS    RESTARTS        AGE
logger-574bd75fd9-wpg4w      1/1     Running   5 (13m ago)     134d
logshipper-7d97c8659-npscd   1/1     Running   26 (5m5s ago)   134d
```
