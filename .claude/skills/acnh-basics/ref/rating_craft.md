# ACNH (v2.0): Island Evaluation and Design Craft

**CONFIRMED** = the cited source states it, or several sources agree. **UNSURE** = sources conflict, the claim has a single weak source, or it is inferred practice. Reddit was not reachable, so community lore is tagged UNSURE.

Key sources: Nookipedia Island evaluation (NI) https://nookipedia.com/wiki/Island_evaluation · Bell Tree "Full Island Rating Guide" (BT, datamine-based) https://www.belltreeforums.com/threads/full-island-rating-guide.509286 · Nintendo Life (NL) https://www.nintendolife.com/guides/animal-crossing-new-horizons-how-to-get-a-5-star-island-rating-and-grow-lily-of-the-valley · TheGamer on Ninji's datamine (TG) https://www.thegamer.com/dataminer-discovers-how-to-get-5-star-island-rating-animal-crossing-new-horizons/

---

## 1. Star rating

### Thresholds (both scores must meet the star level)
| Stars | Development ("Life") | Scenery ("Nature") |
|---|---|---|
| 1 | <80 | <200 |
| 2 | 80–159 | 200–269 |
| 3 | 160–399 | 270–349 |
| 4 | 400–664 | 350–449 |
| 5 | **665+** | **450+** |
CONFIRMED (NI, BT, TG). You need 3★ for K.K. and the Island Designer permit. At 5★ Isabelle sends the golden watering can recipe. CONFIRMED (NI)

### Development points
- Museum +15, Able Sisters +15, upgraded Nook's Cranny +15, **each bridge or incline +15**. CONFIRMED (NI, BT)
- Villagers: 9 → +15, 10 → +30. A full 10 is treated as needed for 5★. CONFIRMED (NI). NL lists 10 as required.
- Weeds: 100 or fewer → +30. Above that the bonus is (1000−weeds)/30, and it hits 0 at 1000 weeds. CONFIRMED (NI)
- **Fences: +0.2 each.** They count, so long fence runs add up. CONFIRMED (NI, BT, NL)
- Bought (non-DIY) furniture placed outdoors: about +1 each. Bonuses: +1 if priced 2,000+ Bells, +2 if over 20,000, **+0.5 for "outdoor" furniture**, plus extra for pieces 3+ tiles wide. CONFIRMED (NI). The exact values differ slightly between NI, BT and NL.
- **Scored per 8×8-tile block (a quarter of a 16×16 acre)**, with a variety formula. BT/NL: fewer than 5 types → count×1; 5–10 types → count×0.5 + types×0.5; 10+ types → count×0.5 + types×0.75. CONFIRMED that blocks are 8×8. The exact coefficients are UNSURE because the sources differ.
- Duplicates: 6 or more of the same item in one 8×8 block → −0.5 for each duplicate; 11 or more → −0.75 each. Customization variants don't count as different items. UNSURE (NI only)
- Wall-mounted items don't count outdoors. CONFIRMED (NI)

### Scenery points
- Fully grown tree or bamboo +1, but only **up to 190 points** (BT, NL). TG/Ninji: **you can't get 5★ with more than 220 trees**, and Isabelle calls the island overgrown. Both caps are UNSURE as exact numbers. Practical target: about 150–190 trees.
- Flowers: bloom +1, stem or bud +0.7, sprout or seed +0.5. Bushes +0.5. Produce plants +0.5 to +1. CONFIRMED (NI, BT)
- **DIY furniture goes into Scenery, not Development**: about +0.25 each, more for pieces 3+ tiles wide, and the same per-8×8 variety logic applies. CONFIRMED for the category. Coefficients UNSURE (NI says it is internally inconsistent).

### Blockers for 5★
- **Cluttered block:** 45 or more of the 64 tiles in an 8×8 block covered. Buildings, bridges, rocks, cliffs, rivers and inclines don't count toward this. CONFIRMED (BT, NL)
- **Litter:** more than 15 dropped (not placed) items on the ground. Branches, shells, stones and star fragments are exempt. CONFIRMED (BT, TG)
- Too many trees (see above).

### Per-acre caps?
- No hard limit on items per acre has been found. The limits work through the 8×8 block rules: variety, duplicate penalties and the 45/64 clutter rule. CONFIRMED that none is listed (NI). UNSURE whether a hidden cap exists.

### Lily of the valley
- In NH it is a **result** of 5★, not a requirement. One spawns about once a day near cliffs while 5★ is kept. CONFIRMED (NL). They grow on cliff tops, one per acre. UNSURE (https://nookipedia.com/wiki/Lily_of_the_valley, which has general wording)

### What this means for design
- **Spread furniture over many 8×8 blocks.** Use 5–10+ different items per block, and never fill 45 or more tiles of a block. Dense "cluttercore" corners can cost you 5★.
- Use DIY items (natural, wooden, garden) for Scenery and bought or Nook Miles outdoor items for Development. Fences are cheap Development points.
- Every bridge or incline is +15. Ten of each is 300 points, so the terrain itself helps the rating.
- Paths are not scored. CONFIRMED (https://www.imore.com/animal-crossing-new-horizons-tips-decorating-your-island)

---

## 2. What the island needs for daily play

### Fixed constraints
- The map is 7×6 = 42 acres of 16×16 tiles (rows A–F from north, columns 1–7). CONFIRMED (https://nookipedia.com/wiki/Acre)
- The airport is always on the south shore and can't be moved. Resident Services sits on the lowest tier and can't be moved. There are 3 natural tiers plus 1 more you can build, which you can't climb. CONFIRMED (https://nookipedia.com/wiki/Town)
- You can't terraform the plaza, the airport dock, beaches, river mouths or the big coastal rocks. CONFIRMED (https://nookipedia.com/wiki/Island_Designer)
- 8 bridges and 8 inclines, raised to **10 each with the v2.0 Pro Construction License**. CONFIRMED (https://nookipedia.com/wiki/Incline, https://nookipedia.com/wiki/Bridge)

### Access
- Villagers can't use ladders or poles, so each river and cliff needs at least one bridge or incline. CONFIRMED (iMore)
- For the player, a ladder or vaulting pole is normal for side areas, and hop spots (1-tile land across water) are a cheap shortcut. CONFIRMED (https://www.thegamer.com/animal-crossing-new-horizons-terraforming-tips-tricks/, akrpg below)
- Designers usually still give the main loop (airport → RS → shops → homes) incline and bridge access, so visitors aren't stuck. UNSURE (community practice; https://acnhislandplanner.blog/acnh-island-layout-ideas/)

### Functional zones (common layouts)
- **Entrance and plaza:** decorate these first, because every visitor sees them. CONFIRMED (https://www.akrpg.com/news/228--animal-crossing-new-horizons-island-design-tips--ideas--layout-terraform-pathway-entrance-custom-design-guide). Keep the airport area and plaza open enough for groups to walk through. UNSURE (layout-ideas blog: don't crowd short entrances)
- **Shop cluster:** Nook's, Able's and the museum near RS, reached from the airport by one clear main route. UNSURE (layout-ideas blog)
- **Rocks and quarry:** there are 6 rocks (one is the money rock), and one respawns per day. Rocks won't spawn near water, cliffs, beach, furniture, flowers, fences, paths or designs. CONFIRMED (https://nookipedia.com/wiki/Rock). Players force rocks into a hidden "quarry" by blocking every other spot. Behind a north cliff or in a fenced corner is typical. UNSURE (https://belltreeforums.com/threads/how-to-force-rocks-to-spawn-where-you-want-them.518999)
- **Flower breeding beds:** flowers must be watered to breed, and running over them can knock them back to buds. Use checkerboard pairs and a path so visitors don't trample them. CONFIRMED (https://nookipedia.com/wiki/Flower; https://play.nintendo.com/news-tips/tips-tricks/animal-crossing-new-horizons-discover-tips/)
- **Resources and catching:** orchard, bamboo patch, open grass and banks for bugs and fish, a clear beach. Keep storage in the house, since more than 15 dropped items counts as litter (BT). UNSURE (community practice)

---

## 3. Design craft

### Workflow
1. Plan on Happy Island Designer (https://eugeneration.github.io/HappyIslandDesigner/) or graph paper. CONFIRMED (https://www.thegamer.com/animal-crossing-new-horizons-terraforming-tips-tricks/)
2. Mark the fixed landmarks (RS, airport, river mouths, beach rocks). Then set one main route, then rough zones, then count bridges and inclines. Detail comes last. CONFIRMED as advice (https://acnhislandplanner.blog/acnh-island-layout-ideas/)
3. Fix house plots before terraforming. Moving a house costs 50,000 Bells. Work one zone at a time. CONFIRMED (https://www.switchbladegaming.com/cozy-games/animal-crossing-island-design-guide/)
4. Clear the ground before editing cliffs. You can't remove a cliff with anything on top of it. CONFIRMED (Island Designer page)
5. Use paths as temporary markers. They show up on the minimap. CONFIRMED (TheGamer terraforming)

### Camera
- Outdoors the camera always faces north. You can only tilt it, and pressing the right stick down gives the top-down view. CONFIRMED (https://nintendowire.com/news/2020/02/27/animal-crossing-new-horizons-to-include-top-down-camera-view/, https://www.gamerevolution.com/?p=648662). Building doors always face south toward the camera. CONFIRMED (gamerevolution)
- What follows from that. Tall items and tall trees hide whatever is north of them, so put tall items at the back (north) and low items in front. A north cliff face works as a backdrop or "wall". A scene is composed for the south-to-north view. A scene you look at from the north side shows only the backs of things. UNSURE (inferred from the fixed camera; widespread designer advice, not directly sourced)

### Scale, density, layering
- Give each zone its own identity, keep one shared palette across the island, and **leave bare grass between zones** so the designed areas stand out. CONFIRMED as advice (Switchblade)
- Path hierarchy: a wide main path in a premium material, a softer secondary path, then narrow garden paths. Semi-transparent dirt edges look worn and natural. CONFIRMED as advice (Switchblade)
- Custom designs with transparent edges go on top of built-in paths to make borders. Lay the tile before you place a fence or simple panel. Simple panels with patterns or wallpaper make walls for open-air buildings. CONFIRMED (https://screenrant.com/animal-crossing-unique-custom-paths-guide/)
- Plant layering (ground cover, shrubs, trees). Loop paths, with dead ends only for photo spots. Rivers at least 3 tiles wide with S-curves. UNSURE (single-source summaries)

### Common beginner mistakes
- Terraforming with no plan, such as boxing Resident Services in with cliffs. Placing houses before shaping the terrain. Redesigning everything at once. CONFIRMED as advice (Switchblade)
- More than about 200 trees, which hurts the rating. Packing houses tightly. Crowding entrances. Trees narrowing paths. Lots of separate land pockets that use up bridges. Cramming furniture onto beaches. Flattening the island with no replacement plan. CONFIRMED as advice (layout-ideas blog)
- Over-cluttering, which can also break the 45/64 rule (BT). Too many themes, items with no context, blocked views, ignoring walk routes. UNSURE (community consensus)

---

## 4. What top islands share (designer guidance)
- **Themed areas with clear entrances.** Arches, gates and fence openings mark where an area starts. Each zone has its own identity inside one shared palette. CONFIRMED that zones and palettes are recommended (Switchblade). Gate-style entrances are UNSURE.
- **Consistent palettes per theme:** cottagecore (brown, green, cream), Nordic (grey, white, dark green), and so on. CONFIRMED (Switchblade)
- **Realistic scale.** Furniture at human scale, simple-panel walls and custom tiled floors make open-air rooms (clinic, café, shop). CONFIRMED that these techniques are used (Screenrant). "Human scale" as a principle is UNSURE.
- **Vertical layering.** Cliffs as upper floors, plus multi-tier waterfalls. CONFIRMED (Screenrant; Switchblade)
- **Night lighting.** Lamps along paths and next to seating, with light reflected in water. UNSURE (low-quality blog only: https://archive.aeon.org/arc/acnh-island-design-tips-tricks-for-crafting-a-dream-island)
