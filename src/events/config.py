import config


class RabbitMQConfig(config.Config):
    """Config for RabbitMQ."""

    host = config.StrField(env="RABBITMQ_HOST", default="localhost")
    port = config.IntField(env="RABBITMQ_PORT", default=5672)
    user = config.StrField(env="RABBITMQ_USER", default="rabbit")
    password = config.StrField(env="RABBITMQ_PASSWORD", default="rabbit")
    vhost = config.StrField(env="RABBITMQ_VHOST", default="/")

    exchange = config.StrField(env="RABBITMQ_EXCHANGE", default="events")
    queue = config.StrField(env="RABBITMQ_QUEUE", default="events")

    @property
    def dsn(self) -> str:
        """DSN for RabbitMQ connection."""
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/{str(self.vhost).strip('/')}"


class AppConfig(config.Config):
    """Application config."""

    debug = config.BoolField(default=False, env="DEBUG")
    rabbitmq = config.NestedField[RabbitMQConfig](RabbitMQConfig)
