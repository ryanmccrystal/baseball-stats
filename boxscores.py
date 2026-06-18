import json

boxscores = {
    "games": []
}

with open("boxscores.json", "w") as f:
    json.dump(boxscores, f, indent=2)

print("Created boxscores.json")
