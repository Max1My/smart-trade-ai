"""Application container."""

import aiogram

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Container, Provider, Singleton

from app.containers.gateways import GatewaysContainer
from app.containers.repositories import RepositoriesContainer
from app.containers.services import ServicesContainer
from config.settings import Settings


class ApplicationContainer(DeclarativeContainer):
    """Application container."""

    wiring_config = WiringConfiguration(
        modules=[

        ]
    )
    config: Configuration = Configuration(default=Settings().model_dump(mode="json"))

    repositories: RepositoriesContainer = Container(  # type: ignore[assignment]
        RepositoriesContainer, config=config
    )
    gateways: GatewaysContainer = Container(GatewaysContainer, config=config)

    services: ServicesContainer = Container(
        ServicesContainer,
        config=config,
        gateways=gateways,
        repositories=repositories,
    )

    dp: Provider[aiogram.Dispatcher] = Singleton(aiogram.Dispatcher)
