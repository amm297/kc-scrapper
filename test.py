from google.cloud import dataproc_v1 as dataproc

from google.cloud.dataproc_v1.gapic.transports import (job_controller_grpc_transport)


def submit_job(project_id, region, cluster_name, bucket, script):
    job_transport = (
        job_controller_grpc_transport.JobControllerGrpcTransport(address=f'{region}-dataproc.googleapis.com:443'))
    job_details = {
        'placement': {
            'cluster_name': cluster_name
        },
        'hive_job': {
            'query_file_uri': f'gs://{bucket}/{script}'
        }
    }
    dataproc_job_client = dataproc.JobControllerClient(job_transport)

    result = dataproc_job_client.submit_job(project_id=project_id, region=region, job=job_details)
    job_id = result.reference.job_id
    print('Submitted job ID {}.'.format(job_id))


def get_params(request, param):
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and param in request_json:
        param_value = request_json[param]
    elif request_args and param in request_args:
        param_value = request_args[param]
    else:
        raise Exception(f'Param {param} not found')
    return param_value


def activate():
    try:
        region = 'europe-west3'
        project_id = 'keepcoding-bootcamp'
        cluster_name = 'kc-bbdd'  # get_params(request, 'name')
        bucket = 'keepcoding-bootcamp'  # get_params(request, 'bucket')
        script = 'scripts/hive.hql'  # get_params(request, 'script')

        return submit_job(project_id, region, cluster_name, bucket, script)
        return 'test'
    except Exception as e:
        print(e)
        return f'Fail to deploy cluster {cluster_name}'


if __name__ == '__main__':
    activate()
