import time

import obsws_python as obs


def main():
    with obs.ReqClient() as client:
        resp = client.get_scene_list()
        scenes = [di.get("sceneName") for di in reversed(resp.scenes)]

        for scene in scenes:
            print(f"Switching to scene {scene}")
            client.set_current_program_scene(scene)
            time.sleep(0.5)


if __name__ == "__main__":
    main()
