#!/usr/bin/env python3
"""
@Author: King
@Date: 2023-05-03 21:46:45
@Email: linsy_king@sjtu.edu.cn
"""

import typer
import os
import shutil
import json
from .updater import Updater

app = typer.Typer(add_completion=False, help="Messenger CLI")


class Messenger:
    config = None

    def __init__(self) -> None:
        """
        Check if `messager.json` exists and load it.
        """
        if os.path.exists("messenger.json"):
            with open("messenger.json", "r") as f:
                self.config = json.load(f)
        else:
            raise Exception(
                "messenger.json not found. Are you in the project initialized by the Messenger? Try `messenger init <your-project-name>`."
            )

    def dump_config(self):
        with open("messenger.json", "w") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def add_scene(self, scene: str):
        if scene in self.config["scenes"] or scene in self.config["sceneprotos"]:
            raise Exception("Scene already exists.")
        self.config["scenes"][scene] = []
        self.dump_config()
        os.mkdir(f"src/Scenes/{scene}")

        Updater(
            [
                ".messenger/scene/Sample/Common.elm",
                ".messenger/scene/Sample/Export.elm",
                ".messenger/scene/Sample/Global.elm",
                ".messenger/scene/Sample/LayerBase.elm",
            ],
            [
                f"src/Scenes/{scene}/Common.elm",
                f"src/Scenes/{scene}/Export.elm",
                f"src/Scenes/{scene}/Global.elm",
                f"src/Scenes/{scene}/LayerBase.elm",
            ],
        ).rep(scene)

    def update_scenes(self):
        """
        Update scene settings (AllScenes and SceneSettings)
        """
        scenes = self.config["scenes"]
        sceneprotos = self.config["sceneprotos"]
        Updater([".messenger/scene/AllScenes.elm"], ["src/Scenes/AllScenes.elm"]).rep(
            "\n".join(
                [
                    f"import Scenes.{l}.Export as {l}\nimport Scenes.{l}.Global as {l}G"
                    for l in scenes
                ]
                + [
                    f"import SceneProtos.{l}.Export as {l}\nimport SceneProtos.{l}.Global as {l}G"
                    for l in sceneprotos
                ]
                + [
                    (
                        "\n".join(
                            f"import Scenes.{l}.Export as {l}"
                            for l in sceneprotos[s]["levels"]
                        )
                    )
                    for s in sceneprotos
                ]
            )
        ).rep(
            ",\n".join(
                [f'( "{l}", {l}G.sceneToST {l}.scene )' for l in scenes]
                + [
                    (
                        ",\n".join(
                            f'( "{l}", {s}G.sceneToST <| {s}.genScene {l}.game )'
                            for l in sceneprotos[s]["levels"]
                        )
                    )
                    for s in sceneprotos
                ]
            )
        )

        Updater(
            [".messenger/scene/SceneSettings.elm"], ["src/Scenes/SceneSettings.elm"]
        ).rep(
            "\n".join(
                [f"import Scenes.{l}.Export as {l}" for l in scenes]
                + [f"import SceneProtos.{l}.Export as {l}" for l in sceneprotos]
            )
        ).rep(
            "\n    | ".join(
                [f"{l}DataT {l}.Data" for l in scenes]
                + [f"{l}DataT {l}.Data" for l in sceneprotos]
            )
        )

    def add_sceneproto(self, scene: str):
        """
        Add a sceneproto
        """
        if scene in self.config["scenes"] or scene in self.config["sceneprotos"]:
            raise Exception("Sceneproto already exists.")
        self.config["sceneprotos"][scene] = {"levels": [], "layers": []}
        self.dump_config()
        os.mkdir(f"src/SceneProtos/{scene}")

        Updater(
            [
                ".messenger/sceneproto/scene/Common.elm",
                ".messenger/sceneproto/scene/Export.elm",
                ".messenger/sceneproto/scene/Global.elm",
                ".messenger/sceneproto/scene/LayerBase.elm",
                ".messenger/sceneproto/scene/LayerInit.elm",
            ],
            [
                f"src/SceneProtos/{scene}/Common.elm",
                f"src/SceneProtos/{scene}/Export.elm",
                f"src/SceneProtos/{scene}/Global.elm",
                f"src/SceneProtos/{scene}/LayerBase.elm",
                f"src/SceneProtos/{scene}/LayerInit.elm",
            ],
        ).rep(scene)

        # Modify Scene
        with open("src/Lib/Scene/Base.elm", "r") as f:
            scenebase = f.read()
        new_scenebase = scenebase.replace(
            "type SceneInitData\n    =",
            f"type SceneInitData\n    = {scene}InitData {scene}Init\n    |",
        ).replace(
            "import Lib.Env.Env exposing (Env)",
            f"import Lib.Env.Env exposing (Env)\nimport SceneProtos.{scene}.LayerInit exposing ({scene}Init)",
        )
        with open("src/Lib/Scene/Base.elm", "w") as f:
            f.write(new_scenebase)

    def add_sceneproto_layer(self, sceneproto: str, layer: str):
        """
        Add a layer in one sceneproto
        """
        if sceneproto not in self.config["sceneprotos"]:
            raise Exception("Sceneproto does not exist.")
        if layer in self.config["sceneprotos"][sceneproto]["layers"]:
            raise Exception("Layer already exists.")
        self.config["sceneprotos"][sceneproto]["layers"].append(layer)
        self.dump_config()
        os.mkdir(f"src/SceneProtos/{sceneproto}/{layer}")

        Updater(
            [
                ".messenger/sceneproto/layer/Model.elm",
                ".messenger/sceneproto/layer/Global.elm",
                ".messenger/sceneproto/layer/Export.elm",
                ".messenger/sceneproto/layer/Common.elm",
            ],
            [
                f"src/SceneProtos/{sceneproto}/{layer}/Model.elm",
                f"src/SceneProtos/{sceneproto}/{layer}/Global.elm",
                f"src/SceneProtos/{sceneproto}/{layer}/Export.elm",
                f"src/SceneProtos/{sceneproto}/{layer}/Common.elm",
            ],
        ).rep(sceneproto).rep(layer)

    def update_sceneproto_layers(self, sceneproto: str):
        """
        Update layers of sceneproto
        """
        layers = self.config["sceneprotos"][sceneproto]["layers"]
        Updater(
            [".messenger/sceneproto/scene/LayerSettings.elm"],
            [f"src/SceneProtos/{sceneproto}/LayerSettings.elm"],
        ).rep(sceneproto).rep(
            "\n".join(
                [f"import SceneProtos.{sceneproto}.{l}.Export as {l}" for l in layers]
            )
        ).rep(
            "\n    | ".join([f"{l}Data {l}.Data" for l in layers])
        )

        Updater(
            [".messenger/sceneproto/scene/Model.elm"],
            [f"src/SceneProtos/{sceneproto}/Model.elm"],
        ).rep(sceneproto).rep(
            "\n".join(
                [
                    f"import SceneProtos.{sceneproto}.{l}.Export as {l}\nimport SceneProtos.{sceneproto}.{l}.Global as {l}G"
                    for l in layers
                ]
            )
        ).rep(
            ",\n".join(
                [
                    f"{l}G.getLayerT <| {l}.initLayer (addCommonData nullCommonData env) NullLayerInitData"
                    for l in layers
                ]
            )
        )

    def add_level(self, sceneproto: str, level: str):
        """
        Add a level generated by sceneproto
        """
        if sceneproto not in self.config["sceneprotos"]:
            raise Exception("Sceneproto does not exist.")
        if level in self.config["sceneprotos"][sceneproto]["levels"]:
            raise Exception("Level already exists.")
        self.config["sceneprotos"][sceneproto]["levels"].append(level)
        self.dump_config()
        os.mkdir(f"src/Scenes/{level}")
        Updater(
            [".messenger/sceneproto/Export.elm"], [f"src/Scenes/{level}/Export.elm"]
        ).rep(level).rep(sceneproto)

    def add_component(self, name: str):
        """
        Add a component
        """
        os.mkdir(f"src/Components/{name}")
        Updater(
            [
                ".messenger/component/Sample/Sample.elm",
                ".messenger/component/Sample/Export.elm",
            ],
            [f"src/Components/{name}/{name}.elm", f"src/Components/{name}/Export.elm"],
        ).rep(name)

    def format(self):
        os.system("elm-format src/ --yes")

    def add_layer(self, scene: str, layer: str):
        """
        Add a layer to a scene
        """
        if scene not in self.config["scenes"]:
            raise Exception("Scene doesn't exist.")
        if layer in self.config["scenes"][scene]:
            raise Exception("Layer already exists.")
        self.config["scenes"][scene].append(layer)
        self.dump_config()
        os.mkdir(f"src/Scenes/{scene}/{layer}")

        Updater(
            [
                ".messenger/layer/Model.elm",
                ".messenger/layer/Global.elm",
                ".messenger/layer/Export.elm",
                ".messenger/layer/Common.elm",
            ],
            [
                f"src/Scenes/{scene}/{layer}/Model.elm",
                f"src/Scenes/{scene}/{layer}/Global.elm",
                f"src/Scenes/{scene}/{layer}/Export.elm",
                f"src/Scenes/{scene}/{layer}/Common.elm",
            ],
        ).rep(scene).rep(layer)

    def update_layers(self, scene: str):
        """
        Update layer settings.
        """
        layers = self.config["scenes"][scene]

        Updater(
            [".messenger/scene/Sample/LayerSettings.elm"],
            [f"src/Scenes/{scene}/LayerSettings.elm"],
        ).rep(scene).rep(
            "\n".join([f"import Scenes.{scene}.{l}.Export as {l}" for l in layers])
        ).rep(
            "\n    | ".join([f"{l}Data {l}.Data" for l in layers])
        )
        Updater(
            [".messenger/scene/Sample/Model.elm"],
            [f"src/Scenes/{scene}/Model.elm"],
        ).rep(scene).rep(
            "\n".join(
                [
                    f"import Scenes.{scene}.{l}.Export as {l}\nimport Scenes.{scene}.{l}.Global as {l}G"
                    for l in layers
                ]
            )
        ).rep(
            ",\n".join(
                [
                    f"{l}G.getLayerT <| {l}.initLayer (addCommonData nullCommonData env) NullLayerInitData"
                    for l in layers
                ]
            )
        )


@app.command()
def init(
    name: str,
    template_repo=typer.Option(
        "https://github.com/linsyking/messenger-templates",
        "--template-repo",
        "-t",
        help="Use customized repository for cloning templates.",
    ),
):
    input(
        f"""Thanks for using Messenger.
See https://github.com/linsyking/Messenger.git for more information.
Here is my plan:
- Create a directory named {name}
- Install the core Messenger liberary
- Install the elm packages needed
Press Enter to continue
"""
    )
    os.makedirs(name, exist_ok=True)
    os.chdir(name)
    os.system(f"git clone {template_repo} .messenger --depth=1")
    shutil.copytree(".messenger/core/", "./src")
    shutil.copytree(".messenger/public/", "./public")
    shutil.copy(".messenger/.gitignore", "./.gitignore")
    shutil.copy(".messenger/Makefile", "./Makefile")
    shutil.copy(".messenger/elm.json", "./elm.json")

    os.makedirs("src/Scenes", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("src/Components", exist_ok=True)
    os.makedirs("src/SceneProtos", exist_ok=True)

    print("Creating elm.json...")
    initObject = {"scenes": {}, "sceneprotos": {}}
    with open("messenger.json", "w") as f:
        json.dump(initObject, f, indent=4, ensure_ascii=False)
    print("Installing dependencies...")
    os.system("elm make")
    print("Done!")
    print(f"Now please go to {name} and add scenes and components.")


@app.command()
def component(name: str):
    msg = Messenger()
    input(f"You are going to create a component named {name}, continue?")
    msg.add_component(name)
    msg.format()
    print("Done!")


@app.command()
def scene(name: str):
    msg = Messenger()
    input(f"You are going to create a scene named {name}, continue?")
    msg.add_scene(name)
    msg.update_scenes()
    msg.format()
    print("Done!")


@app.command()
def layer(scene: str, layer: str):
    msg = Messenger()
    input(
        f"You are going to create a layer named {layer} under scene {scene}, continue?"
    )
    msg.add_layer(scene, layer)
    msg.update_layers(scene)
    msg.format()
    print("Done!")


@app.command()
def sceneproto(sceneproto: str):
    msg = Messenger()
    input(f"You are going to create a sceneproto named {sceneproto}, continue?")
    msg.add_sceneproto(sceneproto)
    msg.format()
    print("Done!")


@app.command()
def level(sceneproto: str, level: str):
    msg = Messenger()
    input(
        f"You are going to create a level named {level} under sceneproto {sceneproto}, continue?"
    )
    msg.add_level(sceneproto, level)
    msg.update_scenes()
    msg.format()
    print("Done!")


@app.command()
def protolayer(sceneproto: str, layer: str):
    msg = Messenger()
    input(
        f"You are going to create a layer named {layer} under sceneproto {sceneproto}, continue?"
    )
    msg.add_sceneproto_layer(sceneproto, layer)
    msg.update_sceneproto_layers(sceneproto)
    msg.format()
    print("Done!")


if __name__ == "__main__":
    app()
