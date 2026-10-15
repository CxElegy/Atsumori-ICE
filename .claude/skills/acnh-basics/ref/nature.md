# ACNH 2.0: nature fundamentals

Scope: version 2.0 only; update 3.0 is ignored. Tags: **C** = CONFIRMED (wiki or datamined guide), **U** = UNSURE (one source, conflicting, or old), **D** = my inference from C facts. Source keys are listed at the end. N = northern hemisphere.

## 1. Trees

| Type | Where | Notes |
|---|---|---|
| Hardwood | grass/dirt | Becomes a cherry blossom tree Apr 1–10 (N) **C** [BF6] |
| Cedar | any land tile; grows naturally on cliff tiers | No regional limit in NH **C** [NP-Tree][BF1]. Lights Dec 15–Jan 6, shake for ornaments **C** [NP-Tree] |
| Fruit | grass/dirt | Apple, cherry, orange, peach, pear. 3 fruit, regrow every 3 days **C** [BF1]. Native + sister (mystery tours) + Mom's fruit **C** [NP-Fruit] |
| Palm | **beach or sand path only**; the only tree that grows on the beach | 2 coconuts every 3 days **C** [BF1][G8-palm][NP-Tree] |
| Bamboo | grass/dirt | Needs 1 free tile around it. Each grown stalk spawns one shoot, once **C** [NP-Bam][BF1] |
| Money tree | the daily shining spot | Grows only "where a tree can normally grow". Bury ≤1k → 3×1k; bury 10k → 70% chance of 3×10k **C** [NP-Money] |

**Growth.** 5 stages (nursery, small, medium, large, adult) at +1 stage per day when unblocked, so a tree is adult 4 days after planting **C** [BF2][NP-Sap]. Game8 says 5 days **U** [G8-space].

**Sapling spacing (datamined, [BF2]):**
- **C** No "blocking" tree may sit in the 3×3 around the tree (all 8 neighbours, diagonals included).
- **C** A sapling planted **directly next to a cliff, water, the beach, a building, an incline or a bridge** never grows.
- **C** Furniture, fences, flowers, shrubs and weeds do **not** block. Game8 agrees for flowers and bushes [G8-space]; Twinfinite says flowers and rocks block. Whether rocks block is **U**.
- **C** A tree is also blocked by **≥12 blocking trees in the 9×9** centred on it.
- **C** A blocking tree is one at the same or a higher stage, counting from stage 2; a stage-1 fruit sapling always blocks. A fruit sapling next to a tree freezes both at their current size.
- **D** On a 2-tile pitch, a sapling has 24 neighbours in its 9×9 and is blocked. On a 3-tile pitch it has 8 and can grow. Grow trees sparse, then move them.

**Adult tree adjacency:**
- **C** An adult tree can be dug up (costs 1 energy from eating) and replanted touching other trees orthogonally or diagonally [BF2][G8-space].
- **C** A tree at stage 2+ **cannot be moved** onto a tile next to a cliff, water, the beach, a building, an incline or a bridge [BF2].
- **C** You can't plant close to a clifftop edge; a glitch gets around this [ACW-cliff].
- **U** Whether touching a cliff or water only diagonally is allowed.
- **C** You can't dig on hard paths, so you can't plant there [NP-IDCP]. A moving-kit glitch allows it, but palms still need sand [G8-path].

**Shaking** (hardwood and cedar only):
- **C** Per day: up to 5 wasp nests, 2 furniture items and 15 bags of 100 Bells. Branches are unlimited [BF3][NP-Tree].
- **C** Acorns and pine cones Sep 1–Dec 10 (N) [BF6].
- **C** Bagworms and spiders also fall out [NP-BugNH].
- **C** Mushrooms appear near hardwood and cedar trees in November [NP-Mush].

**Seasons (N):**
- **C** Cherry blossoms Apr 1–10; maple leaves Nov 16–25; young spring bamboo Feb 25–May 31 [BF6].
- **U** Exact dates for leaf colour and snow. A fan guide gives yellow leaves on Oct 17 and yellow trees on Oct 25 [MTMMO-fall].

**Rating:**
- **C** Each adult tree or bamboo is worth 1 scenery point. 5★ needs 450+ scenery and 665+ development.
- **C** More than **220 points from trees** makes the island "overgrown", which blocks 5★. Stumps don't count [NP-Env][NP-Tree].

## 2. Bushes

- **C** 3 stages: start, nursery, bush. Bushes bloom in season, need no water, and don't breed or spread [BF4][G8-bush].
- **C** They have "no space requirements like trees" and grow anywhere except the beach [BF4].
- **C** They can sit directly next to buildings [NP-Bush].
- **D** So bushes may touch each other, trees and buildings, and hedge rows work.

Bloom windows (N) **C** [NP-Bush][BF4]:
- Camellia (pink, red): Jan 1–Mar 31
- Azalea (pink, white): Apr 11–May 31
- Hydrangea (blue, pink): Jun 1–Jul 20
- Plumeria (pink, white; added in 2.0): Jun 1–Sep 20
- Hibiscus (red, yellow): Jul 21–Sep 20
- Tea olive (orange, yellow): Sep 21–Oct 31
- Holly: Nov 1–Dec 31

No bush blooms during cherry blossom season.

Scenery points per bush: the table says 0.5, the text says 1 **U** [NP-Env]. Snails appear on rocks and bushes in rain **C** [NP-BugNH].

## 3. Flowers and crops

**Species.** 8 species **C** [NP-Flower]:
- Roses: red, white, yellow, pink, orange, purple, black, blue, gold
- Tulips: red, white, yellow, pink, orange, purple, black
- Pansies: red, white, yellow, orange, blue, purple
- Cosmos: red, white, yellow, pink, orange, black
- Lilies: red, white, yellow, pink, orange, black
- Hyacinths: red, white, yellow, pink, orange, blue, purple
- Windflowers: red, white, orange, pink, blue, purple
- Mums: red, white, yellow, pink, purple, green

Lily of the valley appears after **5★ for more than 1 day** **C** [NP-Flower]. Older games put it on cliff tops; NH placement is **U** [NP-LotV].

**Growth and breeding:**
- **C** Seed → stem → bud → bloom takes about 3 days. NH flowers never wilt. Running through flowers can reset blooms to buds; picking a bloom resets it to stems [NP-Flower].
- **C** A flower must be watered to breed. Base offspring chance is 5%, up to 80% with 5 visitors watering [NP-Flower].
- **U** Offspring go to a random empty tile among the 8 neighbours. If all 8 are full, nothing spawns. Partners are same-species flowers in the 3×3 [EEV]. EEV's model is reverse-engineered from play.
- **U** Rain counts as watering.

**Paths.** Soft paths (grass, dirt, dark dirt, sand) let flowers be planted and spread. Hard paths (stone, brick, tile, terra-cotta, wood, any custom design) block both **C** [NP-IDCP].

**Rating.** Seed 0.5, stem/bud 0.7, bloom 1 **C** [NP-Env].

**Mowing.** There is no mowing tool: dig flowers up with a shovel or trample them **C** [NP-Flower].

**Crops.** Pumpkins arrived in 1.5. Version 2.0 added carrots, potatoes, tomatoes, sugarcane and wheat, sold by Leif and Harv's co-op **C** [NP-Prod][BFX7].
- **C** 4 stages at 1 per day, **no space needed**. They grow wherever plants grow except the beach [BFX7].
- **C** Watering gives a yield of 1–3. A picked plant regrows from stage 2. Crops can't be trampled and don't breed or rot [BFX7][NP-Prod].
- **C** Scenery points: start 0.5, ripe 1 [NP-Env].

## 4. Rocks

- **C** There are 6 rocks; 1 is the daily Bell rock, which gives up to 8 hits [NP-Rock][NP-BellRock].
- **C** After eating you can break a rock. Rocks come back **1 per day** at a random spot until there are 6 again [NP-Rock].
- **C** No placement mechanic exists, so you can only steer respawns.
- **C** Rocks won't spawn near the beach, water, cliffs, furniture, shrubs, fences, dropped items, flowers, custom designs, buildings or trees [NP-Rock]. Hard paths also block them [NP-IDCP].
- **U** The community rule is a free 3×3 per rock. Fill every other valid spot, then break a rock to force a respawn [EB-rock].
- **D** A rock garden is one clear grass or dirt patch, with everywhere else covered.

## 5. Weeds, shells, dig spots

**Weeds** **C** [BF5][NP-Weed]:
- Daily spawns: 2 at 0–30 weeds, 1 at 31+, 0 at 150+. Nookipedia says 1 per day.
- Weeds spread more when watered. They spread onto the beach but never spawn there.
- The Beautiful Island ordinance halves spreading.
- Fewer than 100 weeds costs no development points [NP-Env].
- **U** Whether hard paths block weed spawns.

**Shells.** These wash up on the shoreline, about 15 at a time, and refill gradually (**C** for the series, **U** for NH) [NP-Shell]. Hermit crabs hide on the shoreline; wharf roaches sit on beach rocks **C** [NP-BugNH].

**Fossils.** 4 per day, or 6 after a skipped day **C** [NP-Fossil]. Dig spots appear on soft ground only, never on hard paths or designs **C** [NP-IDCP].

## 6. Habitats → design

| Terrain | Species |
|---|---|
| River | 27 river-only fish (dorado, arowana, arapaima…) **C** [NP-FishNH] |
| **Clifftop river** | char, cherry salmon, golden trout, stringfish **C** [NP-FishNH][NP-GT]. Any upper tier works **U** [BTF-tier] |
| River mouth | salmon, king salmon, sturgeon **C** [NP-FishNH][NP-River] |
| Pond | koi, goldfish, gar, giant snakehead… **C** [NP-FishNH] |
| Pier | tuna, blue marlin, giant trevally, mahi-mahi **C** [NP-Pier] |
| Sea | sharks, oarfish…; coelacanth in rain **C** [NP-FishNH] |
| Palms | 8 beetles (horned hercules, horned atlas, golden stag, goliath…) **C** [NP-BugNH][G8-palm] |
| Hardwood/cedar | cicadas; walking leaf under trees **C** [NP-BugNH] |
| Any tree | stag beetles, scarab, atlas moth, walking stick **C** [NP-BugNH] |
| **Stumps** | jewel beetle, violin beetle, citrus long-horned beetle, rosalia batesi **C** [NP-BugNH][NP-Tree] |
| Flowers | orchid mantis (white flowers); peacock butterfly (blue, purple, black); mantis, ladybug, butterflies **C** [NP-BugNH] |
| Water | pondskater, diving beetle, giant water bug; dragonflies and fireflies near water **C** [NP-BugNH] |
| Rocks / lights | pill bug, centipede (from hitting rocks); moth (near lights) **C** [NP-BugNH] |

**Design notes (D):**
- Keep at least 1 upper-tier river.
- Island Designer can't edit river mouths, beaches or beach rocks [NP-IDCP], so design around them.
- Put palms on the beach or on sand-path patches.
- Keep a few stumps.
- Plant white and dark flowers.
- Lots of bushes means rain turns more bug spawns into snails [G8-bush].

## Sources
- NP-Tree https://nookipedia.com/wiki/Tree
- NP-Sap https://nookipedia.com/wiki/Sapling
- NP-Bush https://nookipedia.com/wiki/Bush
- NP-Bam https://nookipedia.com/wiki/Bamboo
- NP-Money https://nookipedia.com/wiki/Money_tree
- NP-Fruit https://nookipedia.com/wiki/Fruit
- NP-Flower https://nookipedia.com/wiki/Flower
- NP-LotV https://nookipedia.com/wiki/Lily_of_the_valley
- NP-Prod https://nookipedia.com/wiki/Produce
- NP-Rock https://nookipedia.com/wiki/Rock
- NP-BellRock https://nookipedia.com/wiki/Bell_rock
- NP-Weed https://nookipedia.com/wiki/Weed
- NP-Shell https://nookipedia.com/wiki/Shell
- NP-Fossil https://nookipedia.com/wiki/Fossil
- NP-IDCP https://nookipedia.com/wiki/Island_Designer_Construction_Permit
- NP-Env https://nookipedia.com/wiki/Environment_rating
- NP-Mush https://nookipedia.com/wiki/Mushroom
- NP-FishNH https://nookipedia.com/wiki/Fish/New_Horizons
- NP-BugNH https://nookipedia.com/wiki/Bug/New_Horizons
- NP-River https://nookipedia.com/wiki/River
- NP-Pier https://nookipedia.com/wiki/Pier
- NP-GT https://nookipedia.com/wiki/Golden_trout
- BF1–BF7 https://bigfootmg.github.io/ACNH-Plant-Guide/ (image pages 02–07, ACNH 2.0.0, datamined)
- BFX7 https://bigfootmg.github.io/ACNH-Plant-Guide/Extras.html (Crops, ex8.png)
- G8-space https://game8.co/games/Animal-Crossing-New-Horizons/archives/287143
- G8-palm https://game8.co/games/Animal-Crossing-New-Horizons/archives/285038
- G8-path https://game8.co/games/Animal-Crossing-New-Horizons/archives/322164
- G8-bush https://game8.co/games/Animal-Crossing-New-Horizons/archives/286618
- ACW-cliff https://animalcrossingworld.com/2020/07/plant-trees-on-cliff-edges-in-animal-crossing-new-horizons-with-this-handy-glitch/
- EEV https://c.eev.ee/acnh-companion/flowers.html
- EB-rock https://expertbeacon.com/why-cant-i-find-rocks-in-animal-crossing/
- BTF-tier https://www.belltreeforums.com/threads/2nd-level-fish-vs-3rd-level-fish.523113
- MTMMO-fall https://www.mtmmo.com/news/868--acnh-october-update--fall-changes-2022--animal-crossing-october-events-items-diys-and-more
- Not directly verified: r/AnimalCrossing (no thread fetched); Twinfinite https://twinfinite.net/2020/03/animal-crossing-new-horizons-tree-spacing-guide/ (seen only in search results)
