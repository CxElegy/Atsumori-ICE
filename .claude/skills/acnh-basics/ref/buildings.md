# ACNH (v2.0): buildings, plots and housing basics

Labels: **C** = CONFIRMED (wiki says it, or two or more independent sources agree). **U** = UNSURE (one fan guide, sources conflict, or my inference).
HID = Happy Island Designer source, commit `68afa9f` (2026-03-11): `app/tools/amenities.ts` and `app/tools/structure.ts` (https://github.com/eugeneration/HappyIslandDesigner). HID sizes are what the editor draws, not game data.

Short names for the sources:
- TG = https://www.thegamer.com/animal-crossing-new-horizons-building-plot-size-guide/
- MT = https://www.mtmmo.com/news/295--animal-crossing-new-horizons-building-plot-sizes-acnh-house-shop-tailor-museum-campsite-exterior-dimensions
- AK = https://www.akrpg.com/news/240--animal-crossing-new-horizons-building-sizes-acnh-structure-dimensions--terraforming-tips
- TU = https://mayohr.tumblr.com/post/617251785956081664/building-footprint-guide-l-x-w (credits a Reddit measurement post)

## 1. Footprints (width × depth in tiles; the door faces south)

| Building | Footprint | Undiggable area in front of the door | Status / sources |
|---|---|---|---|
| Player tent / player house | **5×4** at every upgrade stage | 3×2 strip in front of the door. Paths are allowed there; digging and furniture are not | **C**: HID `playerHouseIcon`/`tentSprite` 5×4; Nookipedia says the tent needs "an unobstructed 5x4 plot" (https://nookipedia.com/wiki/Player_house); TG; TU |
| Does the house get bigger when upgraded? | No. The plot stays 5×4. Before the side rooms are built, "decorative shrubs fill those spaces of the house plot" | – | **C** (Nookipedia Player_house). AK's "6x6/8x8" figures are interior room sizes, not plot sizes |
| Villager house (housing plot) | **4×4** | 3×2 in front of the door (no furniture on the porch; paths OK) | **C**: HID default 4×4; TG; TU; MT. AK says 4×5, which probably counts the porch (U) |
| Resident Services, tent and building | **6×4** in both stages (same spot) | It sits in the plaza | **C**: HID `townhallSprite`/`centerIcon` 6×4; AK |
| RS plaza | **12×10**. In HID the building is centered horizontally at the back of the plaza, with 6 rows of plaza in front of it | No player furniture at all | 12×10 **C** (HID, AK, TU); "no furniture" **C** (https://nookipedia.com/wiki/Plaza); exact offset **U**: AK puts a 1-tile plaza strip behind the building, HID's sprite has none |
| Nook's Cranny, first and upgraded | **7×4** in both stages | AK: 3×2. TU/MT: the "door space matches its full footprint" | 7×4 **C** (HID `nookSprite`, TG: "doesn't increase when you upgrade it"). There is **no tent stage**: Timmy and Tommy sell inside the RS tent until the kit is placed (https://nookipedia.com/wiki/Nook%27s_Cranny). Door area **U** |
| Museum (Blathers' tent, then building) | **7×4** | 3×1 | Building **C** (HID, TG, TU). The tent goes on "the spot chosen by the player" and the museum is built there (https://nookipedia.com/wiki/Museum). The tent's own footprint is **U**, probably the same plot |
| Able Sisters | **5×4** | 3×2 | **C** (HID `ableSprite`, TG, AK). MT says 5×5 (U) |
| Campsite | **4×4** (HID/TG/TU) vs **4×3** (Nookipedia) | 2×1 | **U**: sources conflict. Nookipedia https://nookipedia.com/wiki/Campsite_(facility) says 4x3; plan for 4×4 |
| Airport | **10×6** (HID); MT says "12 wide" | – | **U**. It sits on the south coast, mostly over water (https://nookipedia.com/wiki/Dodo_Airlines) |
| Pier | HID draws it 7×2; "short or long length" varies by island | Steps cannot be decorated | **U** on size. It is on the west or east beach (https://nookipedia.com/wiki/Pier). In 3.0 the pier was extended for the hotel (outside v2.0) |
| Bridge / incline (for reference) | Incline 2×4 (2×1 on top, 2×3 below); bridge 4 wide, spanning 3–5 water tiles | Bridge: 3 open tiles on each side | **C** (TG, AK, MT) |

## 2. Placement rules

- **The whole footprint must be clear.** Another building or furniture inside it blocks placement. Flowers, trees and bushes inside the plot are deleted and not returned. **C** (TG).
- **1-tile gap between buildings**, and between buildings and bridges or inclines, in every direction. Buildings cannot touch side by side. **C** (TU, AK, MT). Paths and furniture can sit right up against a house, except in the plaza. **C** (AK, MT).
- **Trees** need at least 1 free tile between them and a building. **C** (AK, MT).
- **Cliff tops:** you can build on tier 2 and tier 3 "as long as you have the space for it". **C**-ish (https://gamefaqs.gamespot.com/boards/248082-animal-crossing-new-horizons/78503607). The ground must be flat; a plot cannot straddle two levels. **C** by tile logic.
- **Distance from a cliff edge, river or sea:** no source for New Horizons was found. The forum figures (1 tile from the side, 2 from the front) come from **New Leaf** (https://www.belltreeforums.com/threads/how-close-can-villager-houses-be-to-cliffs.387298/). **U**: check in game before planning a building flush against water or a cliff.
- **Beach sand:** AK says "Buildings can be placed on the beach". **U**: only one source.
- **Facing:** every building faces south. There is no rotation. **C** (HID has no rotation for structures; door-front rules are always on the south side).
- **Moving:** the new position **cannot overlap** the old one. **U** (AK only).

## 3. Moving rules

- You can move other residents' houses, Nook's Cranny, the museum, Able Sisters and the campsite. **Resident Services, the plaza and the airport cannot be moved.** **C** (https://nookipedia.com/wiki/Resident_Services; https://nookipedia.com/wiki/Plaza says the plaza "cannot be moved"; the pier and secret beach are fixed per MT).
- **Cost:** your own house 30,000 Bells; other buildings 50,000 Bells each. **C** (TG; https://sportskeeda.com/esports/how-move-house-animal-crossing-new-horizons). (A Nookipedia RS summary said 10,000, likely the plot price.)
- **One relocation per day**, finished the next day. **C** (guides via search: https://progameguides.com/animal-crossing/new-horizons-how-to-relocate-houses-buildings/ is behind a 403, so this is search-snippet only). Moving is unlocked once RS has been upgraded. **C**.
- **Villager plots:** the player places them. "Villagers move into plots placed manually by the player" (https://nookipedia.com/wiki/Villager_house). They are sold at RS ("Sell some land") for **10,000 Bells per plot** (https://gamerguides.com/animal-crossing-new-horizons/guide/walkthrough/day-ten/building-new-house-plots). The maximum is **10 villagers**. **C**. The two starter villagers' tents are also placed by the player with a kit. **C**.
- **Player houses:** one per player profile, **up to 8 on one island**. "8 in New Horizons" (Nookipedia Player_house). **C**. A player cannot own more than one house. **C**.
- **The number of service buildings is fixed:** 1 each of RS, museum, Cranny, Able Sisters and campsite. **C**.

## 4. Things tied to buildings

- **Mailbox:** the player's mailbox "can be picked up, allowing the player to relocate it almost anywhere in town" once the house has been upgraded several times. **C** (Nookipedia Player_house). Mailboxes in front of villager houses are part of the house. **U**.
- **Plaza (12×10, always empty of player items):** events are held here: Bug-Off (Flick's stall), Fishing Tourney (C.J.'s stall), Bunny Day, Fireworks, Halloween, Turkey Day, Toy Day and the Countdown. Event furniture appears there and cannot be moved. **C** (Nookipedia Plaza).
  - **K.K. Slider** plays in the plaza every **Saturday** from 6 PM to midnight. If an event falls on Saturday he moves to Sunday, then Monday. **C** (https://nookipedia.com/wiki/K.K._Slider).
  - **Kicks, Leif, Label** have stalls in the plaza. **C** (Nookipedia Plaza; https://chibisnorlax.github.io/acnhfaq/npc/visiting/).
- **Visitors who wander the island:** Saharah (https://nookipedia.com/wiki/Saharah), Celeste at night (https://nookipedia.com/wiki/Celeste), Redd on his first visit, Wisp, C.J. and Flick on normal visits, and Daisy Mae on Sundays 5–12 (her exact spot is not documented). Wanderers are **U** for C.J., Flick, Wisp and Daisy Mae; **C** for Saharah and Celeste.
- **Redd:** his Treasure Trawler docks at the **secret beach on the north coast**. On his second visit he stands in the plaza. **C** (https://nookipedia.com/wiki/Redd). The secret beach cannot be terraformed or moved. **C** (MT).
- **Gulliver / Gullivarrr:** lie on the main **beach**, and Gulliver's parts are buried along the beach. **C** (https://nookipedia.com/wiki/Gulliver). Whether the beach needs open space for them is **U**. Keep part of the beach empty to be safe.
- **Campsite:** campers stay there; the first is always a smug villager. The visit chance rises to 20% per day. **C** (Nookipedia Campsite_(facility)).
- **Kapp'n** (added in 2.0): his boat is at the **pier**. It needs a 3-star island and K.K.'s first concert, and costs 1,000 Nook Miles. **C** (https://nookipedia.com/wiki/Kapp%27n).
- **Harv's Island** is reached by plane from the airport after meeting Harvey. **C** (Nookipedia Dodo_Airlines).

## 5. Villager house exteriors and behavior

- **Changing a villager's exterior** requires Happy Home Paradise. After finishing the HHP story (about 30 vacation homes), talk to Tom Nook at RS, choose "Let's talk homes", pick the resident's home and pay **9,000 Bells**. You can then change the **exterior** (4 shapes, roof, siding, door, wreath or sign) and the interior. The house **cannot be enlarged**, and the result appears the next day. **C** (https://earth.gamerguides.com/animal-crossing-new-horizons/guide/happy-home-paradise-dlc/gameplay/how-to-unlock-remodelling-for-villagers). Whether a new shape changes the 4×4 plot is not stated. **U**; most likely it stays 4×4.
- **Player house exterior** (roof, door, mailbox, shape) is changed at RS for 5,000 Bells, or free once all loans are paid. **C** (Nookipedia Player_house).
- **Villager interiors** are always 6×6. **C** (Nookipedia Villager_house).
- **Villager movement:** villagers walk freely on grass and paths and **do not need paths**. Paths are cosmetic. **U** (no explicit source). They cannot walk through furniture or fences. A house fenced off completely risks trapping villagers. **U**: leave the 3×2 porch and a walkable route open.

