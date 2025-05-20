

# Execution
## Starting Ollama Server
```sh
ollama serve
ollama run deepseek-r1
```

## Starting Server
```sh
cd server
python -m src.main
```


# Development
## TODO
- [x] Load query arguments from config not requests
- [x] include user id and workspace id in requests
- [x] fix re-render bug that make it impossible to change currnetWorkspaceId
- [x] Tag search using workspace ID too
- [x] Switch workspace in frontend
- [ ] avoid repeated recommendations (bookmarked or previously recommended in same chat) -> add filter in RAG?

## Database Management
The script provides options to manage the database and fetch data using command-line arguments.

### Command-Line Arguments
`--reset_db` or `-r`: Reset the database.
`--fetch_everything` or `-e`: Fetch all data.
`--fetch_headline` or `-hl`: Fetch headline data.
`--hours_count` or `-hr`: Specify the number of hours to fetch data from (default is 12 hours).

### Example Usage
To reset the database and fetch all data from the last 24 hours:
```sh
python script.py --reset_db --fetch_everything --hours_count 24
```



# Quick Performnace Log
some referential information about the performance of application for documentation use
 

## RAG Input
- Option 1: ask LLM to parse the query to generate keywords 
- Option 2: use user's query directly
- Option 3: ask LLM to rephrase user's query to generate better sentence for RAG

currently selected: option 3

## Output Article Ranking
- Option 1: use rank from rag directly
- Option 2: let llm do the selection
  - Gemma normal performance
  - GPT shows much better performance

currently selected: option 2


# Frontend
## Message Format
/*{
      index: 1,
      sender: "Bot",
      content: "Good morning, here are some recommendations for you",
      news: [
        {
          title: "News Title",
          summary: "News Summary",
          link: "https://www.example.com",
          timestamp: "2021-10-01T12:00:00Z",
          site: "example.com",
          bookmarked: false,
        },
        {
          title: "News Title2",
          summary: "News Summary22",
          link: "https://www.example.com",
          timestamp: "2021-10-11T12:00:00Z",
          site: "example.com",
          bookmarked: true,
        }
      ],
    },
    {
      index: 2,
      sender: "User",
      content: "Thank you",
      news: [],
    },*/


# A nice example!
## Demo
any cool games recommend? 
hmmm thats cool, any for xbox?


## Example 2
User Query: "give me some news about nintendo switch!"

LLM Revised query for RAG: Recent news and updates about Nintendo Switch games and features.

2025-03-27 01:53:15,868 - INFO - Retrieved 10 documents
2025-03-27 01:53:15,869 - INFO - Retrieved document 0 - Nintendo reportedly has three-phase launch plan for Switch 2 games - Eurogamer
2025-03-27 01:53:15,869 - INFO - Retrieved document 1 - The 10 games that defined the Nintendo Switch - Polygon
2025-03-27 01:53:15,869 - INFO - Retrieved document 2 - Xbox Is Experimenting With An Extra Button Press To Open Games - Kotaku
2025-03-27 01:53:15,869 - INFO - Retrieved document 3 - Xbox testing new Game Hubs feature, update rolling out to select users now - Windows Central      
2025-03-27 01:53:15,869 - INFO - Retrieved document 4 - 5 Obscure Nintendo consoles you’ve likely never heard of
2025-03-27 01:53:15,869 - INFO - Retrieved document 5 - Nintendo Reuploads Game Vouchers Trailer With Switch 2 Fine Print - Nintendo Life
2025-03-27 01:53:15,870 - INFO - Retrieved document 6 - Apple Seeds iOS 18.4 RC Ahead of Official Release in Early April
2025-03-27 01:53:15,870 - INFO - Retrieved document 7 - Apple is launching 15+ new products later this year, here’s what’s coming - 9to5Mac
2025-03-27 01:53:15,870 - INFO - Retrieved document 8 - Xbox sale round-up March 25, 2025 - TrueAchievements
2025-03-27 01:53:15,870 - INFO - Retrieved document 9 - Big Publishers And Studios Are Scrambling To Avoid GTA 6's Launch - Kotaku

2025-03-27 01:53:16,924 - INFO - Took 1.0539512634277344 seconds to generate response: <result>[0, 1, 5]</result>
2025-03-27 01:53:16,924 - INFO - Selected indices: [0, 1, 5]

Response
[
    {
        "id": "30853a7b-ac80-49df-92db-9c941afbba0c",
        "metadata": {
            "description": "Nintendo will reportedly have a three phase launch plan for its Switch 2 games.",
            "fetch_date": "2025-03-27T01:42:04.828849",
            "publish_date": "2025-03-25T15:45:44Z",
            "source": "Eurogamer.net",
            "title": "Nintendo reportedly has three-phase launch plan for Switch 2 games - Eurogamer",
            "url": "https://www.eurogamer.net/nintendo-reportedly-has-three-phase-launch-plan-for-switch-2-games"
        },
        "page_content": "Nintendo is planning a phased launch for its upcoming Switch 2, with three distinct phases. Initially, the first phase will feature exclusive first-party titles released in June, aligning with industry predictions. Following this, the second phase will heavily involve third-party studios, with most expecting access to a dev kit by June. The final phase, concluding with the holiday period, is projected to coincide with the release of November and December. While details remain scarce, an April Nintendo Direct is slated to reveal the release date and price of the new console.  Expect further updates on games like Metroid Prime 4 and Silksong, though fans should remain cautiously optimistic regarding the full release timeline.",
        "type": "Document"
    },
    {
        "id": "f92cef3f-60dc-4d1b-a221-ac714037dfa4",
        "metadata": {
            "description": "From Animal Crossing to Mario Kart, Zelda to Hollow Knight, the console’s key games tell the story of a changing Nintendo",
            "fetch_date": "2025-03-27T01:42:04.828849",
            "publish_date": "2025-03-25T13:00:00Z",
            "source": "Polygon",
            "title": "The 10 games that defined the Nintendo Switch - Polygon",
            "url": "https://www.polygon.com/nintendo/545093/nintendo-switch-most-important-games"
        },
        "page_content": "Here's a summary of the game list:\n\nThis list analyzes the success of various games on Nintendo Switch, highlighting key trends and observations. The list demonstrates Nintendo’s strategic approach to game development, prioritizing hit games early on and leveraging the platform’s reach. While some titles, like Tetris 99 and Fire Emblem: Three Houses, faced challenges, others, like Hollow Knight and Hades, thrived due to their strong indie appeal and strong community support. The list also touches on the impact of the Switch’s popularity on the wider gaming landscape.",
        "type": "Document"
    },
    {
        "id": "d1a94dc8-6bea-424d-99c7-f20399f8e88f",
        "metadata": {
            "description": "ICYMI: Vouchers won't work on Switch 2",
            "fetch_date": "2025-03-26T19:12:26.769226",
            "publish_date": "2025-03-25T04:55:00Z",
            "source": "Nintendo Life",
            "title": "Nintendo Reuploads Game Vouchers Trailer With Switch 2 Fine Print - Nintendo Life",
            "url": "https://www.nintendolife.com/news/2025/03/nintendo-reuploads-game-vouchers-trailer-with-switch-2-fine-print"
        },
        "page_content": "Nintendo has clarified its Game Voucher policy for the Switch 2, addressing concerns about exclusive game vouchers. Previously, Nintendo announced the vouchers wouldn't be valid for Switch 2 exclusives. Now, in a significant update, they’ve reuploaded the YouTube trailer, explicitly stating these vouchers are not redeemable for Switch 2 games and cannot be combined with other offers.\n\nWhile this limitation impacts the original incentive for purchasing the vouchers, users should still be able to access all currently available games on the Switch 2. This move reflects a strategic consideration of backwards compatibility, offering continued access to beloved titles. It's a necessary adjustment to ensure a balanced experience for existing Switch owners.",
        "type": "Document"
    }
]