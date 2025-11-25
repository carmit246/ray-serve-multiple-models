# ray-serve-multiple-models
Ray Server demo with multiple models on local kind cluster

## 1. Install Kind and run a cluster
```
brew install kind
kind create cluster
```

## 2. Build & Load the Image
```bash
docker build -t ray_multiple_models:1.0 -f Dockerfile.multiple .
kind load docker-image ray_multiple_models:1.0
```

## 3. Deploy Ray Operator & Service
```bash
kubectl create ns ray
helm repo add kuberay https://ray-project.github.io/kuberay-helm
helm install kuberay-operator kuberay/kuberay-operator
kubectl apply -f multiple-models-rayService.yaml
```

## 4. Test Endpoints
port-forward
```
kubectl port-forward svc/serve-multiple-models-head-svc 8000:8000&
```
Test LLM endpoint:
```
curl http://localhost:8000/llm/answer?text=%22the%20capital%20of%20Italy?%22"
```
Test sentiment analysis endpoint:
```
curl http://localhost:8000/sentiment/sentiment?text=%22this%20miovie%20is%20bad%22
curl http://localhost:8000/sentiment/sentiment?text=%22this%20miovie%20is%20amazing%22"
```

## 5. Check Ray Dashboard
```
kubectl port-forward svc/serve-multiple-models-head-svc 8265:8265&
```

## 6. Install Prometheus
```
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace -f prometheus.yaml
```
```
kubectl port-forward svc/prometheus-grafana 3000:80
```
Load dashboards from this repository 

## 7. Create Load

```bash
urls=(
  "curl http://localhost:8000/sentiment/sentiment?text=%22this%20miovie%20is%20bad%22"
  "curl http://localhost:8000/llm/answer?text=%22the%20capital%20of%20Italy?%22"
)

for i in {1..30}; do
  for j in {1..6}; do
    printf "%s\n" "${urls[@]}"
  done | xargs -n 1 -P 12 -I {} bash -c 'curl -s "{}" > /dev/null && echo "Called: {}"'
  echo "Batch $i done"
  sleep 2
done
```

### Check number of replicas and performance in Grafana and Ray dashboard
