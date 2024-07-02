# Load the Tilt extensions
load('ext://namespace', 'namespace_create', 'namespace_inject')

# Define the Kubernetes YAML files to be used
yamls = [
    'kubernetes/01-namespace.yaml',
    'kubernetes/02-secrets.yaml',
    'kubernetes/03-zookeeper-deployment.yaml',
    'kubernetes/04-kafka-broker-deployment.yaml',
    'kubernetes/05-synchronizer-deployment.yaml',
    'kubernetes/06-discord-deployment.yaml',
    'kubernetes/07-checker-deployment.yaml',
    'kubernetes/08-kresus-deployment.yaml',
]

namespace_create('firefly-iii-dev')

# Define the local Docker builds
docker_build('firefly-synchro-synchronizer-dev', './common', dockerfile='common/synchronizer.Dockerfile')
docker_build('firefly-synchro-discord-dev', './common', dockerfile='common/discord.Dockerfile')
docker_build('firefly-synchro-checker-dev', './common', dockerfile='common/checker.Dockerfile')
docker_build('firefly-synchro-notify-dev', './common', dockerfile='common/notify.Dockerfile')
docker_build('firefly-synchro-kresus-dev', './common', dockerfile='common/kresus.Dockerfile')

# Inject namespace into the YAML files
for yaml in yamls:
    namespace_inject(yaml, 'firefly-iii-dev')

# Load the YAML files into Tilt
k8s_yaml(yamls)

# Replace the images in the YAML files with the locally built images
k8s_image_json_path('firefly-synchro-synchronizer-dev', '{.spec.template.spec.containers[?(@.name=="synchronizer")].image}', kind='Deployment')
k8s_image_json_path('firefly-synchro-discord-dev', '{.spec.template.spec.containers[?(@.name=="discord")].image}', kind='Deployment')
k8s_image_json_path('firefly-synchro-checker-dev', '{.spec.template.spec.containers[?(@.name=="checker")].image}', kind='Deployment')
k8s_image_json_path('firefly-synchro-notify-dev', '{.spec.template.spec.containers[?(@.name=="notify")].image}', kind='Deployment')
k8s_image_json_path('firefly-synchro-kresus-dev', '{.spec.template.spec.containers[?(@.name=="kresus")].image}', kind='Deployment')

# Configure the Kubernetes resources
k8s_resource('firefly-synchro-synchronizer', port_forwards=8000)
k8s_resource('firefly-synchro-discord', port_forwards=8001)
k8s_resource('firefly-synchro-checker', port_forwards=8002)
k8s_resource('kresus', port_forwards=8083)

# Uncomment and set up the resource if needed
# k8s_resource('notify-deployment', port_forwards=8004)

# Optionally: Add any additional configurations or commands
# e.g., local_resource('db-migrations', 'python manage.py migrate')
