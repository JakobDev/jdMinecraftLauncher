#!/usr/bin/env python
import argparse
import json


def encrypt(text: str)-> str:
    text = text[::-1]
    output = ""
    for c in text:
        output += chr(ord(c) + 5)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clientID", required=True, help="Your clientID")
    parser.add_argument("--secret", required=True, help="Your clientSecret")
    parser.add_argument("--redirectURL", required=True, help="Your redirectURL")
    parser.add_argument("--output", required=True, help="The output file")
    args = parser.parse_args().__dict__

    data = {"encrypted": True}
    data["clientID"] = encrypt(args["clientID"])
    data["secret"] = encrypt(args["secret"])
    data["redirectURL"] = encrypt(args["redirectURL"])

    with open(args["output"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
