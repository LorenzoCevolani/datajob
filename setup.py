# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datajob', 'datajob.glue', 'datajob.package', 'datajob.stepfunctions']

package_data = \
{'': ['*']}

install_requires = \
['aws-cdk.aws-glue>=1.87.1,<2.0.0',
 'aws-cdk.aws-s3-deployment>=1.87.1,<2.0.0',
 'aws-cdk.cloudformation-include>=1.87.1,<2.0.0',
 'aws-cdk.core>=1.87.1,<2.0.0',
 'aws-empty-bucket>=2.4.0,<3.0.0',
 'contextvars>=2.4,<3.0',
 'dephell>=0.8.3,<0.9.0',
 'rich>=9.13.0,<10.0.0',
 'stepfunctions>=1.1.2,<2.0.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['datajob = datajob.datajob:run']}

setup_kwargs = {
    'name': 'datajob',
    'version': '0.7.0',
    'description': 'Build and deploy a serverless data pipeline with no effort on AWS.',
    'long_description': '![logo](./assets/logo.png)\n\n<div align="center">\n <b>Build and deploy a serverless data pipeline on AWS with no effort.</b></br>\n <i>Our goal is to let developers think about the business logic, datajob does the rest...</i>\n </br>\n </br>\n </br>\n</div>\n\n\n- We support creating and deploying code to python shell / pyspark Glue jobs.\n- Orchestrate the glue jobs using stepfunctions as simple as `task1 >> [task2,task3] >> task4`\n- Let us [know](https://github.com/vincentclaes/datajob/discussions) what you want to see next.\n\n> Dependencies are [AWS CDK](https://github.com/aws/aws-cdk) and [Step Functions SDK for data science](https://github.com/aws/aws-step-functions-data-science-sdk-python) <br/>\n\n# Installation\n\n Datajob can be installed using pip. <br/>\n Beware that we depend on [aws cdk cli](https://github.com/aws/aws-cdk)!\n\n    pip install datajob\n    npm install -g aws-cdk@1.98.0 # latest version of datajob depends this version\n\n# Quickstart\n\nWe have a simple data pipeline composed of [2 glue jobs](./examples/data_pipeline_with_packaged_project/glue_jobs/) orchestrated sequentially using step functions.\n\n```python\nimport pathlib\nfrom aws_cdk import core\n\nfrom datajob.datajob_stack import DataJobStack\nfrom datajob.glue.glue_job import GlueJob\nfrom datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow\n\n\ncurrent_dir = pathlib.Path(__file__).parent.absolute()\n\napp = core.App()\n\n\nwith DataJobStack(scope=app, id="data-pipeline-pkg", project_root=current_dir) as datajob_stack:\n\n    task1 = GlueJob(\n        datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py"\n    )\n\n    task2 = GlueJob(\n        datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py"\n    )\n\n    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as step_functions_workflow:\n        task1 >> task2\n\napp.synth()\n\n```\n\nWe add the above code in a file called `datajob_stack.py` in the [root of the project](./examples/data_pipeline_with_packaged_project/).\n\n\n### Configure CDK\nFollow the steps [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config) to configure your credentials.\n\n```shell script\nexport AWS_PROFILE=default\n# use the aws cli to get your account number\nexport AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)\nexport AWS_DEFAULT_REGION=us-east-2\n\ncdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION\n```\n\n### Deploy\n\n```shell\nexport STAGE=$AWS_ACCOUNT\ncd examples/data_pipeline_with_packaged_project\ndatajob deploy --config datajob_stack.py --stage $STAGE --package setuppy\n```\nDatajob will create s3 buckets based on the `stage` variable.\nThe stage variable will typically be something like "dev", "stg", "prd", ...\nbut since S3 buckets need to be globally unique, for this example we will use our `$AWS_ACCOUNT` for the `--stage` parameter.\n\n<details>\n<summary>use cdk cli</summary>\n\n```shell script\ncd examples/data_pipeline_with_packaged_project\npython setup.py bdist_wheel\ncdk deploy --app  "python datajob_stack.py" -c stage=$STAGE\n```\n</details>\n\n### Run\n\n```shell script\ndatajob execute --state-machine data-pipeline-pkg-$STAGE-workflow\n```\nThe step function state machine name is constructed as `<datajob_stack.id>-<stage>-<step_functions_workflow.name>`.\nThe terminal will show a link to the step functions page to follow up on your pipeline run.\n\n### Destroy\n\n```shell script\ndatajob destroy --config datajob_stack.py --stage $STAGE\n```\n\n<details>\n<summary>use cdk cli</summary>\n\n```shell script\ncdk destroy --app  "python datajob_stack.py" -c stage=$STAGE\n```\n</details>\n\n> Note: you can use any cdk arguments in the datajob cli\n\n# Functionality\n\n<details>\n<summary>Using datajob\'s S3 data bucket</summary>\n\nDynamically reference the `datajob_stack` data bucket name to the arguments of your GlueJob by calling\n`datajob_stack.context.data_bucket_name`.\n\n```python\nimport pathlib\n\nfrom aws_cdk import core\nfrom datajob.datajob_stack import DataJobStack\nfrom datajob.glue.glue_job import GlueJob\nfrom datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow\n\ncurrent_dir = str(pathlib.Path(__file__).parent.absolute())\n\napp = core.App()\n\nwith DataJobStack(\n    scope=app, id="datajob-python-pyspark", project_root=current_dir\n) as datajob_stack:\n\n    pyspark_job = GlueJob(\n        datajob_stack=datajob_stack,\n        name="pyspark-job",\n        job_path="glue_job/glue_pyspark_example.py",\n        job_type="glueetl",\n        glue_version="2.0",  # we only support glue 2.0\n        python_version="3",\n        worker_type="Standard",  # options are Standard / G.1X / G.2X\n        number_of_workers=1,\n        arguments={\n            "--source": f"s3://{datajob_stack.context.data_bucket_name}/raw/iris_dataset.csv",\n            "--destination": f"s3://{datajob_stack.context.data_bucket_name}/target/pyspark_job/iris_dataset.parquet",\n        },\n    )\n\n    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as sfn:\n        pyspark_job >> ...\n\n```\n\ndeploy to stage `my-stage`:\n\n```shell\ndatajob deploy --config datajob_stack.py --stage my-stage --package setuppy\n```\n\n`datajob_stack.context.data_bucket_name` will evaluate to `datajob-python-pyspark-my-stage`\n\nyou can find this example [here](./examples/data_pipeline_pyspark/glue_job/glue_pyspark_example.py)\n\n</details>\n\n<details>\n<summary>Deploy files to deployment bucket</summary>\n\nSpecify the path to the folder we would like to include in the deployment bucket.\n\n```python\n\nfrom aws_cdk import core\nfrom datajob.datajob_stack import DataJobStack\n\napp = core.App()\n\nwith DataJobStack(\n    scope=app, id="some-stack-name", include_folder="path/to/folder/"\n) as datajob_stack:\n\n    ...\n\n```\n\n</details>\n\n<details>\n<summary>Package project</summary>\n\nPackage you project using [poetry](https://python-poetry.org/)\n\n```shell\ndatajob deploy --config datajob_stack.py --package poetry\n```\nPackage you project using [setup.py](./examples/data_pipeline_with_packaged_project)\n```shell\ndatajob deploy --config datajob_stack.py --package setuppy\n```\n</details>\n\n<details>\n<summary>Using Pyspark</summary>\n\n```python\nimport pathlib\n\nfrom aws_cdk import core\nfrom datajob.datajob_stack import DataJobStack\nfrom datajob.glue.glue_job import GlueJob\nfrom datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow\n\ncurrent_dir = str(pathlib.Path(__file__).parent.absolute())\n\napp = core.App()\n\nwith DataJobStack(\n    scope=app, id="datajob-python-pyspark", project_root=current_dir\n) as datajob_stack:\n\n    pyspark_job = GlueJob(\n        datajob_stack=datajob_stack,\n        name="pyspark-job",\n        job_path="glue_job/glue_pyspark_example.py",\n        job_type="glueetl",\n        glue_version="2.0",  # we only support glue 2.0\n        python_version="3",\n        worker_type="Standard",  # options are Standard / G.1X / G.2X\n        number_of_workers=1,\n        arguments={\n            "--source": f"s3://{datajob_stack.context.data_bucket_name}/raw/iris_dataset.csv",\n            "--destination": f"s3://{datajob_stack.context.data_bucket_name}/target/pyspark_job/iris_dataset.parquet",\n        },\n    )\n```\nfull example can be found in [examples/data_pipeline_pyspark](examples/data_pipeline_pyspark]).\n</details>\n\n<details>\n<summary>Orchestrate stepfunctions tasks in parallel</summary>\n\n```python\n# task1 and task2 are orchestrated in parallel.\n# task3 will only start when both task1 and task2 have succeeded.\n[task1, task2] >> task3\n```\n\n</details>\n\n<details>\n<summary>Orchestrate 1 stepfunction task</summary>\n\nUse the [Ellipsis](https://docs.python.org/dev/library/constants.html#Ellipsis) object to be able to orchestrate 1 job via step functions.\n\n```python\nsome_task >> ...\n```\n\n</details>\n\n\n# Datajob in depth\n\nThe `datajob_stack` is the instance that will result in a cloudformation stack.\nThe path in `project_root` helps `datajob_stack` locate the root of the project where\nthe setup.py/poetry pyproject.toml file can be found, as well as the `dist/` folder with the wheel of your project .\n\n```python\nimport pathlib\nfrom aws_cdk import core\n\nfrom datajob.datajob_stack import DataJobStack\n\ncurrent_dir = pathlib.Path(__file__).parent.absolute()\napp = core.App()\n\nwith DataJobStack(\n    scope=app, id="data-pipeline-pkg", project_root=current_dir\n) as datajob_stack:\n\n    ...\n```\n\nWhen __entering the contextmanager__ of DataJobStack:\n\nA [DataJobContext](./datajob/datajob_stack.py#L48) is initialized\nto deploy and run a data pipeline on AWS.\nThe following resources are created:\n1) "data bucket"\n    - an S3 bucket that you can use to dump ingested data, dump intermediate results and the final output.\n    - you can access the data bucket as a [Bucket](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_s3/Bucket.html) object via ```datajob_stack.context.data_bucket```\n    - you can access the data bucket name via ```datajob_stack.context.data_bucket_name```\n2) "deployment bucket"\n   - an s3 bucket to deploy code, artifacts, scripts, config, files, ...\n   - you can access the deployment bucket as a [Bucket](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_s3/Bucket.html) object via ```datajob_stack.context.deployment_bucket```\n   - you can access the deployment bucket name via ```datajob_stack.context.deployment_bucket_name```\n\nwhen __exiting the context manager__ all the resources of our DataJobStack object are created.\n\n<details>\n<summary>We can write the above example more explicitly...</summary>\n\n```python\nimport pathlib\nfrom aws_cdk import core\n\nfrom datajob.datajob_stack import DataJobStack\nfrom datajob.glue.glue_job import GlueJob\nfrom datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow\n\napp = core.App()\n\ncurrent_dir = pathlib.Path(__file__).parent.absolute()\n\napp = core.App()\n\ndatajob_stack = DataJobStack(scope=app, id="data-pipeline-pkg", project_root=current_dir)\ndatajob_stack.init_datajob_context()\n\ntask1 = GlueJob(datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py")\ntask2 = GlueJob(datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py")\n\nwith StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as step_functions_workflow:\n    task1 >> task2\n\ndatajob_stack.create_resources()\napp.synth()\n```\n</details>\n\n# Ideas\n\nAny suggestions can be shared by starting a [discussion](https://github.com/vincentclaes/datajob/discussions)\n\nThese are the ideas, we find interesting to implement;\n\n- add a time based trigger to the step functions workflow.\n- add an s3 event trigger to the step functions workflow.\n- add a lambda that copies data from one s3 location to another.\n- add an sns that notifies in case of any failure (slack/email)\n- version your data pipeline.\n- cli command to view the logs / glue jobs / s3 bucket\n- implement sagemaker services\n    - processing jobs\n    - hyperparameter tuning jobs\n    - training jobs\n- implement lambda\n- implement ECS Fargate\n- create a serverless UI that follows up on the different pipelines deployed on possibly different AWS accounts using Datajob\n\n> [Feedback](https://github.com/vincentclaes/datajob/discussions) is much appreciated!\n',
    'author': 'Vincent Claes',
    'author_email': 'vincent.v.claes@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vincentclaes/datajob',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)

