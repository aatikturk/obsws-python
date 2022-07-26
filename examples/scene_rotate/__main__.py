import time

import obsstudio_sdk as obs


def main():
    resp = cl.get_scene_list()
    scenes = reversed(tuple(di["sceneName"] for di in resp["scenes"]))

    for sc in scenes:
        print(f"Switching to scene {sc}")
        cl.set_current_program_scene(sc)
        time.sleep(0.5)


if __name__ == "__main__":
    cl = obs.ReqClient()

    main()
