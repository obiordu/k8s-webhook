from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/validate")
async def validate(request: Request):
    """
    Validate admission requests
    """
    try:
        body = await request.json()
        request_info = body.get("request", {})
        
        # Extract relevant information
        object_info = request_info.get("object", {})
        namespace = object_info.get("metadata", {}).get("namespace", "default")
        name = object_info.get("metadata", {}).get("name", "")
        kind = object_info.get("kind", "")
        
        logger.info(f"Validating {kind} {namespace}/{name}")
        
        # Perform validation
        allowed = True
        message = "Validation successful"
        
        # Check for required labels
        metadata = object_info.get("metadata", {})
        labels = metadata.get("labels", {})
        
        if not labels.get("app"):
            allowed = False
            message = "Missing required label: app"
        
        # Check container security context
        if kind.lower() == "pod":
            containers = object_info.get("spec", {}).get("containers", [])
            for container in containers:
                security_context = container.get("securityContext", {})
                
                # Ensure privileged mode is not enabled
                if security_context.get("privileged", False):
                    allowed = False
                    message = f"Container {container['name']} cannot run in privileged mode"
                    break
                
                # Ensure root user is not used
                if not security_context.get("runAsNonRoot", False):
                    allowed = False
                    message = f"Container {container['name']} must run as non-root user"
                    break
        
        response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": body.get("request", {}).get("uid", ""),
                "allowed": allowed,
                "status": {
                    "message": message
                }
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )

@app.post("/mutate")
async def mutate(request: Request):
    """
    Mutate admission requests
    """
    try:
        body = await request.json()
        request_info = body.get("request", {})
        
        # Extract relevant information
        object_info = request_info.get("object", {})
        namespace = object_info.get("metadata", {}).get("namespace", "default")
        name = object_info.get("metadata", {}).get("name", "")
        kind = object_info.get("kind", "")
        
        logger.info(f"Mutating {kind} {namespace}/{name}")
        
        # Initialize patch operations
        patches = []
        
        # Add default labels if missing
        metadata = object_info.get("metadata", {})
        labels = metadata.get("labels", {})
        
        if not labels.get("environment"):
            patches.append({
                "op": "add",
                "path": "/metadata/labels/environment",
                "value": "production"
            })
        
        # Add default resource limits if missing
        if kind.lower() == "pod":
            containers = object_info.get("spec", {}).get("containers", [])
            for i, container in enumerate(containers):
                if not container.get("resources"):
                    patches.append({
                        "op": "add",
                        "path": f"/spec/containers/{i}/resources",
                        "value": {
                            "limits": {
                                "cpu": "500m",
                                "memory": "512Mi"
                            },
                            "requests": {
                                "cpu": "100m",
                                "memory": "128Mi"
                            }
                        }
                    })
        
        response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": body.get("request", {}).get("uid", ""),
                "allowed": True,
                "patchType": "JSONPatch" if patches else None,
                "patch": patches if patches else None
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )

@app.get("/")
async def root():
    """
    Root endpoint for health check
    """
    return {"status": "healthy"}

@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8443,
        ssl_keyfile="./certs/webhook-key.pem",
        ssl_certfile="./certs/webhook-cert.pem"
    )
