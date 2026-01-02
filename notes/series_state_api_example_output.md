# Series State API Example Output

This document shows example outputs from running `scripts/series_state_api.py` with different series IDs.

## Example Run: Series ID 2616372 (T1 vs Gen.G Esports)

### Command
```bash
python3 scripts/series_state_api.py 2616372
```

### Current Output (with LoL-specific fragments)

The script currently uses League of Legends-specific GraphQL fragments (`SeriesTeamStateLol`, `SeriesPlayerStateLol`, `GameTeamStateLol`, `GamePlayerStateLol`) which are not recognized by the API schema, resulting in validation errors:

```
🔍 Querying Series State API for Series ID: 2616372

❌ Errors:
   - Validation error (UnknownType@[seriesState/teams]) : Unknown type 'SeriesTeamStateLol'
   - Validation error (UnknownType@[seriesState/teams/players]) : Unknown type 'SeriesPlayerStateLol'
```

### Error Response Structure

When the script encounters these errors, the JSON response structure is:

```json
{
  "errors": [
    {
      "message": "Validation error (UnknownType@[seriesState/teams]) : Unknown type 'SeriesTeamStateLol'",
      "locations": [
        {
          "line": 23,
          "column": 24
        }
      ],
      "path": [
        "seriesState",
        "teams"
      ],
      "extensions": {
        "classification": "ValidationError",
        "errorType": "BAD_REQUEST",
        "errorDetail": "INVALID_ARGUMENT"
      }
    },
    {
      "message": "Validation error (UnknownType@[seriesState/teams/players]) : Unknown type 'SeriesPlayerStateLol'",
      "locations": [
        {
          "line": 36,
          "column": 28
        }
      ],
      "path": [
        "seriesState",
        "teams",
        "players"
      ],
      "extensions": {
        "classification": "ValidationError",
        "errorType": "BAD_REQUEST",
        "errorDetail": "INVALID_ARGUMENT"
      }
    }
  ]
}
```

## Successful Query Output (Basic Query)

When using a basic query without LoL-specific fragments, the API returns successful data. Here's the structure and example:

### Successful Response Structure

```json
{
  "data": {
    "seriesState": {
      "id": "2616372",
      "version": "3.1",
      "title": {
        "nameShortened": "lol"
      },
      "format": "best-of-3",
      "started": true,
      "finished": true,
      "valid": true,
      "startedAt": "2024-01-17T10:59:00Z",
      "teams": [...],
      "games": [...]
    }
  }
}
```

### Example Full Response (Series ID 2616372)

#### Series-Level Information

- **Series ID**: `2616372`
- **Version**: `3.1`
- **Title**: League of Legends (`lol`)
- **Format**: `best-of-3`
- **Status**: Started and Finished
- **Started At**: `2024-01-17T10:59:00Z`

#### Teams Summary

**Team 1: T1**
- **Team ID**: `47494`
- **Score**: 1 (lost)
- **Total Kills**: 26
- **Total Deaths**: 47
- **Players**:
  - Zeus (ID: 23596): 6/9/16 (K/D/A)
  - Oner (ID: 21690): 5/11/12
  - Faker (ID: 20763): 4/11/15
  - Gumayusi (ID: 24427): 9/7/9
  - Keria (ID: 26121): 2/9/20

**Team 2: Gen.G**
- **Team ID**: `47558`
- **Score**: 2 (won)
- **Total Kills**: 47
- **Total Deaths**: 26
- **Players**:
  - Kiin (ID: 21335): 5/9/13
  - Canyon (ID: 21233): 4/2/25
  - Chovy (ID: 22958): 17/5/18
  - Peyz (ID: 24653): 18/5/14
  - Lehends (ID: 20972): 2/5/26

#### Games Breakdown

**Game 1** (Sequence: 1)
- **Map**: Summoner's Rift
- **Winner**: T1 (Score: 6-5)
- **T1 (Red Side)**: Won
  - Zeus: Gwen - 3/2/3
  - Oner: Jarvan IV - 2/0/3
  - Faker: Neeko - 1/3/5
  - Gumayusi: Lucian - 0/0/4
  - Keria: Milio - 0/0/5
- **Gen.G (Blue Side)**: Lost
  - Kiin: K'Sante - 1/2/0
  - Canyon: Rell - 0/0/3
  - Chovy: Corki - 2/1/2
  - Peyz: Aphelios - 1/2/2
  - Lehends: Lulu - 0/1/2

**Game 2** (Sequence: 2)
- **Map**: Summoner's Rift
- **Winner**: Gen.G (Score: 17-10)
- **T1 (Blue Side)**: Lost
  - Zeus: Udyr - 1/2/8
  - Oner: Lee Sin - 1/4/4
  - Faker: Azir - 0/5/5
  - Gumayusi: Nilah - 6/3/3
  - Keria: Senna - 2/3/7
- **Gen.G (Red Side)**: Won
  - Kiin: K'Sante - 3/4/4
  - Canyon: Maokai - 1/1/12
  - Chovy: Tristana - 8/2/7
  - Peyz: Varus - 5/2/8
  - Lehends: Rakan - 0/1/12

**Game 3** (Sequence: 3)
- **Map**: Summoner's Rift
- **Winner**: Gen.G (Score: 25-10)
- **T1 (Blue Side)**: Lost
  - Zeus: Kennen - 2/5/5
  - Oner: Bel'Veth - 2/7/5
  - Faker: Azir - 3/3/5
  - Gumayusi: Jhin - 3/4/2
  - Keria: Bard - 0/6/8
- **Gen.G (Red Side)**: Won
  - Kiin: Udyr - 1/3/9
  - Canyon: Maokai - 3/1/10
  - Chovy: Yone - 7/2/9
  - Peyz: Varus - 12/1/4
  - Lehends: Rakan - 2/3/12

## Key Observations

### Available Fields (Basic Query)

The following fields are available without LoL-specific fragments:

**Series Level:**
- `id`, `version`, `title.nameShortened`, `format`
- `started`, `finished`, `valid`, `startedAt`

**Team Level (Series):**
- `id`, `name`, `score`, `won`
- `kills`, `deaths`
- `players[]` with: `id`, `name`, `kills`, `deaths`, `killAssistsGiven`

**Game Level:**
- `id`, `sequenceNumber`, `started`, `finished`
- `map.name`
- `teams[]` with: `id`, `name`, `side`, `won`, `score`, `kills`, `deaths`
- `players[]` with: `id`, `name`, `kills`, `deaths`, `killAssistsGiven`, `character.id`, `character.name`

### Unavailable Fields (Current API Version)

The following fields require LoL-specific fragments that are not recognized:
- `SeriesTeamStateLol`: `damageDealt`, `damageTaken`, `visionScore`, `kdaRatio`, `totalMoneyEarned`
- `SeriesPlayerStateLol`: `damageDealt`, `damageTaken`, `damagePercentage`, `visionScore`, `kdaRatio`, `totalMoneyEarned`, `character`
- `GameTeamStateLol`: `damageDealt`, `damageTaken`, `visionScore`, `baronPowerPlays`
- `GamePlayerStateLol`: `damageDealt`, `damageTaken`, `damagePercentage`, `visionScore`, `kdaRatio`, `totalMoneyEarned`, `moneyPerMinute`, `damagePerMinute`, `respawnClock`

### Version-Specific Fields

Some fields require newer API versions:
- `forfeited`: Requires version 3.48+
- `duration` (series level): Requires version 3.14+
- `startedAt` (game level): Requires version 3.7+
- `duration` (game level): Requires version 3.15+

## Recommendations

1. **Remove LoL-specific fragments** from the default query in `series_state_api.py` to make it work with the current API schema
2. **Make fragments conditional** based on the series title or API version
3. **Add version detection** to request appropriate fields based on the API version
4. **Use basic query first** to get core data, then optionally request extended fields if available

## Example Usage

To get a successful response, use a basic query without LoL-specific fragments:

```python
query = """
query SeriesState($seriesId: ID!) {
    seriesState(id: $seriesId) {
        id
        version
        title { nameShortened }
        format
        started
        finished
        teams {
            id
            name
            score
            won
            kills
            deaths
            players {
                id
                name
                kills
                deaths
                killAssistsGiven
            }
        }
        games {
            id
            sequenceNumber
            started
            finished
            map { name }
            teams {
                id
                name
                side
                won
                score
                kills
                deaths
                players {
                    id
                    name
                    kills
                    deaths
                    killAssistsGiven
                    character {
                        id
                        name
                    }
                }
            }
        }
    }
}
"""
```

Note: The `character` field is available at the game level but not at the series team level.

