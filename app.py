#!/usr/bin/env python3

from aws_cdk import core

from cloud_playground.cloud_playground_stack import CloudPlaygroundStack


app = core.App()
CloudPlaygroundStack(app, "cloud-playground")

app.synth()
