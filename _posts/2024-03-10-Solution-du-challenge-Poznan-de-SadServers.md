---
title: "Solution du challenge Poznań de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Poznań": Helm Chart Issue in Kubernetes

**Level:** Medium

**Type:** Fix

**Tags:** [kubernetes](https://sadservers.com/tag/kubernetes)  

**Description:** A DevOps engineer created a Helm Chart web-chart with a custom nginx site, however he still gets the default nginx *index.html*.

You can check for example with `POD_IP=$(kubectl get pods -n default -o jsonpath='{.items[0].status.podIP}')` and `curl -s "${POD_IP}">`.

In addition, he should set replicas to `3`.

The chart is not working as expected. Fix the configurations, so you get the custom HTML page from any nginx pod.

Root access is not needed ("admin" user cannot sudo).

Credit [Kamil Błaż](https://www.devkblaz.com/)

**Test:** Doing curl on the default port (:80) of any nginx pod returns a `Welcome SadServers` page. The "Check My Solution" button runs the script `/home/admin/agent/check.sh`, which you can see and execute.

**Time to Solve:** 15 minutes.

Tous les fichiers helm sont regroupés dans le dossier `web_chat` :

```console
admin@i-051bc370604c4a393:~$ ls -Rl web_chart/
web_chart/:
total 12
-rw-r--r-- 1 admin admin  114 Feb 26 01:35 Chart.yaml
drwxr-xr-x 2 admin admin 4096 Feb 26 01:36 templates
-rw-r--r-- 1 admin admin  184 Feb 26 01:35 values.yaml

web_chart/templates:
total 12
-rw-r--r-- 1 admin admin 235 Feb 26 01:36 configmap.yaml
-rw-r--r-- 1 admin admin 551 Feb 26 01:35 deployment.yaml
-rw-r--r-- 1 admin admin 341 Feb 26 01:36 service.yaml
```

Sur le système, je remarque un conteneur docker, mais il s'agit du registry :

```console
admin@i-051bc370604c4a393:~$ docker ps -a
CONTAINER ID   IMAGE        COMMAND                  CREATED       STATUS              PORTS                                       NAMES
313c4db27012   registry:2   "/entrypoint.sh /etc…"   13 days ago   Up About a minute   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   docker-registry
```

Je vois aussi un Nginx qui écoute en local, évidemment ce n'est pas celui qui nous intéresse.

```console
admin@i-051bc370604c4a393:~/web_chart$ ps aux | grep nginx
root        2333  0.0  0.2  32660  5024 ?        Ss   13:37   0:00 nginx: master process nginx -g daemon off;
systemd+    2454  0.0  0.1  33116  3156 ?        S    13:37   0:00 nginx: worker process
admin       3671  0.0  0.0   5264   640 pts/0    S<+  13:51   0:00 grep nginx
```

Avec `kubectl` je vois un pod qui tourne :

```console
admin@i-05973edec9df3b9dd:~$ kubectl describe pods
Name:             web-chart-nginx-c867f54dc-c6z9g
Namespace:        default
Priority:         0
Service Account:  default
Node:             node1/172.31.36.94
Start Time:       Mon, 26 Feb 2024 01:36:45 +0000
Labels:           app=nginx
                  pod-template-hash=c867f54dc
Annotations:      <none>
Status:           Running
IP:               10.42.0.19
IPs:
  IP:           10.42.0.19
Controlled By:  ReplicaSet/web-chart-nginx-c867f54dc
Containers:
  web-chart:
    Container ID:   containerd://68165e9c1b4883db65435c9a72b59dee6cb6560fe3701017a3aa61f8a0016b1f
    Image:          localhost:5000/nginx:1.17.0
    Image ID:       localhost:5000/nginx@sha256:079aa93463d2566b7a81cbdf856afc6d4d2a6f9100ca3bcbecf24ade92c9a7fe
    Port:           80/TCP
    Host Port:      0/TCP
    State:          Running
      Started:      Sun, 10 Mar 2024 13:57:58 +0000
    Last State:     Terminated
      Reason:       Unknown
      Exit Code:    255
      Started:      Mon, 26 Feb 2024 01:36:48 +0000
      Finished:     Sun, 10 Mar 2024 13:57:52 +0000
    Ready:          True
    Restart Count:  1
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-dq7b2 (ro)
Conditions:
  Type              Status
  Initialized       True 
  Ready             True 
  ContainersReady   True 
  PodScheduled      True 
Volumes:
  kube-api-access-dq7b2:
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
  Type     Reason          Age   From               Message
  ----     ------          ----  ----               -------
  Normal   Scheduled       13d   default-scheduler  Successfully assigned default/web-chart-nginx-c867f54dc-c6z9g to node1
  Normal   Pulling         13d   kubelet            Pulling image "localhost:5000/nginx:1.17.0"
  Normal   Pulled          13d   kubelet            Successfully pulled image "localhost:5000/nginx:1.17.0" in 2.867s (2.867s including waiting)
  Normal   Created         13d   kubelet            Created container web-chart
  Normal   Started         13d   kubelet            Started container web-chart
  Warning  FailedMount     25s   kubelet            MountVolume.SetUp failed for volume "kube-api-access-dq7b2" : object "default"/"kube-root-ca.crt" not registered
  Normal   SandboxChanged  25s   kubelet            Pod sandbox changed, it will be killed and re-created.
  Normal   Pulled          24s   kubelet            Container image "localhost:5000/nginx:1.17.0" already present on machine
  Normal   Created         24s   kubelet            Created container web-chart
  Normal   Started         23s   kubelet            Started container web-chart
```

Le script de vérification du challenge récupère l'IP de ce pod et effectue une requête sur son port 80 pour voir la réponse.

```console
#!/usr/bin/bash
# DO NOT MODIFY THIS FILE ("Check My Solution" will fail)

helm get values web-chart | grep -q "replicaCount: 3"
GET_REPLICAS=$?
POD_IP=$(kubectl get pods -n default -o jsonpath='{.items[0].status.podIP}')
curl -s "${POD_IP}" | grep -q "Welcome SadServers"
CHECK_WEB_SERVER=$?

if [[ "${GET_REPLICAS}" -eq 0 ]] && [[ "${CHECK_WEB_SERVER}" -eq 0 ]]; then
    echo -n "OK"
else
    echo -n "NO"
fi
```

Avec la commande suivante on peut voir que le pod est configuré pour n'avoir qu'une seule replica (instance) :

```console
admin@i-051bc370604c4a393:~$ helm get values web-chart
USER-SUPPLIED VALUES:
image:
  pullPolicy: IfNotPresent
  repository: localhost:5000/nginx
  tag: 1.17.0
replicaCount: 1
service:
  name: nginx-service
  port: 8080
  targetPort: 9000
  type: ClusterIP
```

Le numéro de release est indiqué dans le fichier `Chart.yaml`, ici `0.1.0`.

```yaml
apiVersion: v2
name: web-chart
description: Helm Chart Nginx
type: application
version: 0.1.0
appVersion: "1.0.0"
```

Dans le fichier `values.yaml` on voit l'image utilisée ainsi que sa configuration :

```yaml
replicaCount: 1

image:
  repository: localhost:5000/nginx
  tag: "1.17.0"
  pullPolicy: IfNotPresent

service:
  name: nginx-service
  type: ClusterIP
  port: 8080
  targetPort: 9000
```

Dans `templates/configmap.yaml` on trouve la configuration qui doit normalement placer le contenu HTML où il faut...

{% raw %}
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-cm-index-html
  namespace: default
data:
  index.html: |
    <html>
    <h1>Welcome SadServers</h1>
    </br>
    <h1>Hi! I got deployed successfully</h1>
    </html>
```
{% endraw %}

Pour terminer, le fichier `templates/deployment.yaml` rassemble les différentes resources que l'on a vu via des références :

{% raw %}
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-nginx
  labels:
    app: nginx
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
```
{% endraw %}

Ce qu'on peut noter ici, c'est que le fichier configmap ne semble pas inclus dans le déploiement.

Si on se connecte au pod pour chercher le fichier `index.html` on constate en effet qu'il n'a pas été remplacé :

```console
admin@i-05973edec9df3b9dd:~$ kubectl exec -it web-chart-nginx-c867f54dc-c6z9g /bin/sh
kubectl exec [POD] [COMMAND] is DEPRECATED and will be removed in a future version. Use kubectl exec [POD] -- [COMMAND] instead.
# find / -name "index.html"
/usr/share/nginx/html/index.html
find: '/proc/7/map_files': Permission denied
# cat /usr/share/nginx/html/index.html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

`kubectl` a bien connaissance de l'entrée configmap, mais il manque une relation avec le pod.

```console
admin@i-05973edec9df3b9dd:~$ kubectl get configmaps -n default
NAME                      DATA   AGE
kube-root-ca.crt          1      21d
web-chart-cm-index-html   1      13d
admin@i-05973edec9df3b9dd:~$ kubectl describe configmap web-chart-cm-index-html -n default
Name:         web-chart-cm-index-html
Namespace:    default
Labels:       app.kubernetes.io/managed-by=Helm
Annotations:  meta.helm.sh/release-name: web-chart
              meta.helm.sh/release-namespace: default

Data
====
index.html:
----
<html>
<h1>Welcome SadServers</h1>
</br>
<h1>Hi! I got deployed successfully</h1>
</html>


BinaryData
====

Events:  <none>
```

Pour corriger ça il faut rajouter un volume qui utilise le configMap :

{% raw %}
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-nginx
  labels:
    app: nginx
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      volumes:
        - name: config-volume
          configMap:
            name: web-chart-cm-index-html
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          volumeMounts:
            - name: config-volume
              mountPath: /usr/share/nginx/html/
```
{% endraw %}

Il faut aussi changer la version de la release dans `Chart.yaml`. On peut ensuite faire un nouveau paquet :

```bash
admin@i-0de01eeb4911ab689:~$ helm package web_chart
Successfully packaged chart and saved it to: /home/admin/web-chart-0.1.1.tgz
admin@i-0de01eeb4911ab689:~$ helm upgrade web-chart /home/admin/web-chart-0.1.1.tgz
Release "web-chart" has been upgraded. Happy Helming!
NAME: web-chart
LAST DEPLOYED: Sun Mar 10 14:35:09 2024
NAMESPACE: default
STATUS: deployed
REVISION: 2
TEST SUITE: Non
```

Cette fois, on obtient le bon contenu :

```console
admin@i-0de01eeb4911ab689:~$ kubectl get pods
NAME                              READY   STATUS    RESTARTS   AGE
web-chart-nginx-d5ff548b9-dn6wq   1/1     Running   0          50s
admin@i-0de01eeb4911ab689:~$ ./agent/check.sh 
NOadmin@i-0de01eeb4911ab689:~POD_IP=$(kubectl get pods -n default -o jsonpath='{.items[0].status.podIP}')')
admin@i-0de01eeb4911ab689:~$ echo $POD_IP
10.42.0.21
admin@i-0de01eeb4911ab689:~$ curl http://10.42.0.21
<html>
<h1>Welcome SadServers</h1>
</br>
<h1>Hi! I got deployed successfully</h1>
</html>
```

Il aura aussi fallu que je force le changement de replicas (édité dans `values.yaml`) avec cette commande :

```console
admin@i-0de01eeb4911ab689:~$ helm upgrade web-chart /home/admin/web-chart-0.1.1.tgz -f web_chart/values.yaml
Release "web-chart" has been upgraded. Happy Helming!
NAME: web-chart
LAST DEPLOYED: Sun Mar 10 14:41:25 2024
NAMESPACE: default
STATUS: deployed
REVISION: 3
TEST SUITE: None
```
