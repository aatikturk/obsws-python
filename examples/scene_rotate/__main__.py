import time

import obsws_python as obs


def main():
    resp = cl.get_scene_list()
    scenes = reversed(tuple(di.get("sceneName") for di in resp.scenes))

    for scene in scenes:
        print(f"Switching to scene {scene}")
        cl.set_current_program_scene(scene)
        time.sleep(0.5)


if __name__ == "__main__":
    cl = obs.ReqClient()

    main()
