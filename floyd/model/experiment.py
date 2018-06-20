from marshmallow import Schema, fields, post_load
from pytz import utc

from floyd.constants import PST_TIMEZONE
from floyd.date_utils import pretty_date
from floyd.model.base import BaseModel


class ExperimentSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    created = fields.DateTime()
    description = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    # TODO: change to not allow none
    mode = fields.Str(allow_none=True)
    duration = fields.Number(allow_none=True)
    log_id = fields.Str(load_from="logId")
    canvas = fields.Dict(load_only=True)
    task_instances = fields.List(fields.Str(), dump_only=True)
    instance_type = fields.Str(load_from="instanceType", allow_none=True)
    service_url = fields.Str(load_from="serviceUrl", allow_none=True)
    tensorboard_url = fields.Str(load_from="tensorboardUrl", allow_none=True)
    output_id = fields.Str(load_from="instanceOutputId", allow_none=True)
    instance_log_id = fields.Str(load_from="instanceLogId", allow_none=True)
    timeout_seconds = fields.Integer(allow_none=True)
    latest_metrics = fields.Dict(load_from="latest_metrics", allow_none=True)

    @post_load
    def make_experiment(self, data):
        return Experiment(**data)


class Experiment(BaseModel):
    schema = ExperimentSchema(strict=True)

    def __init__(self,
                 id,
                 name,
                 description,
                 created,
                 state,
                 duration,
                 log_id,
                 canvas=None,
                 instance_type=None,
                 service_url=None,
                 tensorboard_url=None,
                 output_id=None,
                 instance_log_id=None,
                 timeout_seconds=None,
                 latest_metrics=None,
                 mode=None):
        self.id = id
        self.name = name
        self.description = description
        self.created = self.localize_date(created)
        self.state = state
        self.duration = duration
        self.log_id = log_id
        if canvas:
            nodes = canvas.get('nodes', {})
            self.task_instances = {}
            for key in nodes:
                self.task_instances[nodes[key].get("taskInstanceId")] = nodes[key].get("type")
        self.instance_type = instance_type
        self.service_url = service_url
        self.tensorboard_url = tensorboard_url
        self.output_id = output_id
        self.instance_log_id = instance_log_id
        self.timeout_seconds = timeout_seconds
        self.latest_metrics = latest_metrics
        self.mode = mode

    def localize_date(self, date):
        if not date.tzinfo:
            date = utc.localize(date)
        return date.astimezone(PST_TIMEZONE)

    def to_dict(self):
        return self.__dict__

    @property
    def created_pretty(self):
        return pretty_date(self.created)

    @property
    def duration_rounded(self):
        return int(self.duration or 0)

    @property
    def instance_type_trimmed(self):
        if self.instance_type:
            return self.instance_type.split('_')[0]
        return self.instance_type

    @property
    def is_finished(self):
        return self.state in ["shutdown", "failed", "success", "timeout"]


class ExperimentRequestSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    module_id = fields.Str()
    full_command = fields.Str()
    data_ids = fields.List(fields.Str)
    family_id = fields.Str(allow_none=True)
    instance_type = fields.Str(allow_none=True)
    env = fields.Str(allow_none=True)
    max_runtime = fields.Integer(allow_none=True)
    yaml_config = fields.Str()
    task = fields.Str()

    @post_load
    def make_experiment_request(self, kwargs):
        return ExperimentRequest(**kwargs)


class ExperimentRequest(BaseModel):
    schema = ExperimentRequestSchema(strict=True)

    def __init__(self,
                 name,
                 description,
                 module_id,
                 full_command,
                 env=None,
                 data_ids=None,
                 family_id=None,
                 instance_type=None,
                 max_runtime=None,
                 yaml_config=None,
                 task=None):
        self.name = name
        self.description = description
        self.full_command = full_command
        self.module_id = module_id
        self.data_ids = data_ids if data_ids is not None else []
        self.family_id = family_id
        self.instance_type = instance_type
        self.env = env
        self.max_runtime = max_runtime
        self.yaml_config = yaml_config
        self.task = task
