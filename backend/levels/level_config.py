"""
SQL Detective Game - Level Configuration
Contains all 7 level definitions with stories, objectives, and expected queries
"""
from typing import Dict, List, Any


class Level:
    """Represents a single level in the game"""
    
    def __init__(
        self,
        level_id: int,
        title: str,
        story: str,
        objective: str,
        hint: str,
        sql_concepts: List[str],
        tables_unlocked: List[str],
        expected_query: str,
        expected_columns: List[str] = None,
        expected_row_count: int = None,
        order_matters: bool = False
    ):
        self.level_id = level_id
        self.title = title
        self.story = story
        self.objective = objective
        self.hint = hint
        self.sql_concepts = sql_concepts
        self.tables_unlocked = tables_unlocked
        self.expected_query = expected_query
        self.expected_columns = expected_columns
        self.expected_row_count = expected_row_count
        self.order_matters = order_matters
    
    def to_dict(self, include_solution: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        data = {
            'id': self.level_id,
            'title': self.title,
            'story': self.story,
            'objective': self.objective,
            'hint': self.hint,
            'sql_concepts': self.sql_concepts,
            'tables_unlocked': self.tables_unlocked
        }
        if include_solution:
            data['expected_query'] = self.expected_query
        return data


# =============================================================================
# LEVEL DEFINITIONS
# =============================================================================

LEVELS: Dict[int, Level] = {
    
    # =========================================================================
    # LEVEL 1: The Missing Witness (SELECT + WHERE)
    # =========================================================================
    1: Level(
        level_id=1,
        title="The Missing Witness",
        story="""
        🔍 CASE FILE #2024-0315: The Downtown Bank Heist
        
        Detective, we have a serious situation. Last night, $2.5 million was stolen 
        from the Downtown Bank vault. The security system was disabled from inside,
        suggesting an inside job or someone with inside knowledge.
        
        A key witness who may have seen the perpetrators has gone missing. We need 
        to narrow down our suspect list. Intelligence suggests we should focus on 
        individuals over 30 with prior criminal history - they match the profile 
        of experienced criminals capable of such a sophisticated heist.
        
        The department has granted you access to the SUSPECTS database.
        Start your investigation now.
        """,
        objective="Find all suspects who are over 30 years old AND have a criminal record.",
        hint="Use SELECT with WHERE clause. The 'criminal_record' column uses 1 for yes, 0 for no.",
        sql_concepts=["SELECT", "WHERE", "AND"],
        tables_unlocked=["suspects"],
        expected_query="""
            SELECT * FROM suspects 
            WHERE age > 30 AND criminal_record = 1
        """,
        expected_columns=None,  # Any columns acceptable
        expected_row_count=2,   # Viktor (42) and James (45) have records
        order_matters=False
    ),
    
    # =========================================================================
    # LEVEL 2: The Midnight Call (BETWEEN, ORDER BY, LIMIT)
    # =========================================================================
    2: Level(
        level_id=2,
        title="The Midnight Call",
        story="""
        🔍 CASE FILE #2024-0315: Phone Records Analysis
        
        Excellent work identifying our primary suspects! Now we need to trace 
        their communications.
        
        The robbery occurred at 11:45 PM on March 15, 2024. Our surveillance team 
        believes crucial coordination calls were made between 11 PM and 2 AM that night.
        
        You now have access to PHONE_RECORDS. Find the most recent calls made 
        during this critical window. The perpetrators likely made last-minute 
        coordination calls right before the heist.
        
        Time is of the essence - we need the 5 most recent calls from that window.
        """,
        objective="Find the 5 most recent phone calls made between 11 PM (March 15) and 2 AM (March 16, 2024).",
        hint="Use BETWEEN for the timestamp range, ORDER BY timestamp DESC, and LIMIT 5.",
        sql_concepts=["BETWEEN", "ORDER BY", "LIMIT", "DESC"],
        tables_unlocked=["suspects", "phone_records"],
        expected_query="""
            SELECT * FROM phone_records 
            WHERE timestamp BETWEEN '2024-03-15 23:00:00' AND '2024-03-16 02:00:00'
            ORDER BY timestamp DESC
            LIMIT 5
        """,
        expected_columns=None,
        expected_row_count=5,
        order_matters=True
    ),
    
    # =========================================================================
    # LEVEL 3: The Connection (INNER JOIN)
    # =========================================================================
    3: Level(
        level_id=3,
        title="The Connection",
        story="""
        🔍 CASE FILE #2024-0315: CCTV Analysis
        
        The phone records revealed suspicious activity. But we need physical proof.
        
        Our tech team has recovered CCTV footage from the Downtown Bank area.
        We've run facial recognition on the footage and logged all identified 
        individuals in the database.
        
        You now have access to CCTV_LOGS and LOCATIONS tables. We need to find 
        out which of our suspects were physically present at or near the 
        Downtown Bank on the night of the robbery.
        
        Cross-reference the CCTV logs with suspect data. This is where we 
        connect the dots.
        """,
        objective="Find all suspects who were captured on CCTV at 'Downtown Bank'. Show their name, occupation, location, and timestamp.",
        hint="Use INNER JOIN to connect suspects with cctv_logs and locations tables. Filter by location name.",
        sql_concepts=["INNER JOIN", "Foreign Keys", "Multi-table queries"],
        tables_unlocked=["suspects", "phone_records", "cctv_logs", "locations"],
        expected_query="""
            SELECT s.name, s.occupation, l.name as location, c.timestamp
            FROM suspects s
            INNER JOIN cctv_logs c ON s.id = c.person_id
            INNER JOIN locations l ON c.location_id = l.id
            WHERE l.name = 'Downtown Bank'
        """,
        expected_columns=['name', 'occupation', 'location', 'timestamp'],
        expected_row_count=5,  # Multiple sightings at bank
        order_matters=False
    ),
    
    # =========================================================================
    # LEVEL 4: The Pattern (GROUP BY, HAVING)
    # =========================================================================
    4: Level(
        level_id=4,
        title="The Pattern",
        story="""
        🔍 CASE FILE #2024-0315: Communication Pattern Analysis
        
        We've identified multiple suspects at the scene. But who was coordinating?
        
        Criminal psychologists tell us that the mastermind typically makes 
        unusually high number of calls before a major operation - coordinating 
        team members, confirming plans, issuing final instructions.
        
        Our phone records contain all calls from March 15, 2024. We need to 
        identify anyone who made an unusually high number of calls that day.
        
        Find callers who made MORE than 5 calls on the day of the crime.
        This should reveal who was doing the coordination.
        """,
        objective="Find all callers who made more than 5 calls on March 15, 2024. Show the caller_id and their total call count.",
        hint="Use GROUP BY caller_id, COUNT(*), and HAVING to filter groups. Use DATE() to extract the date from timestamp.",
        sql_concepts=["GROUP BY", "HAVING", "COUNT", "Aggregate functions"],
        tables_unlocked=["suspects", "phone_records", "cctv_logs", "locations"],
        expected_query="""
            SELECT caller_id, COUNT(*) as call_count
            FROM phone_records
            WHERE DATE(timestamp) = '2024-03-15'
            GROUP BY caller_id
            HAVING COUNT(*) > 5
        """,
        expected_columns=['caller_id', 'call_count'],
        expected_row_count=1,  # Viktor (id=3) made many calls
        order_matters=False
    ),
    
    # =========================================================================
    # LEVEL 5: The Money Trail (Subqueries)
    # =========================================================================
    5: Level(
        level_id=5,
        title="The Money Trail",
        story="""
        🔍 CASE FILE #2024-0315: Financial Investigation
        
        Excellent detective work! We've identified Viktor Petrov as the likely 
        coordinator. But we need to prove motive and trace the money.
        
        Criminals often make large transactions before and after a heist - 
        preparing equipment, paying accomplices, or moving stolen funds.
        
        You now have access to BANK_TRANSACTIONS. We're looking for 
        transactions that are ABOVE AVERAGE for the week of the crime 
        (March 10-17, 2024). These large transactions may indicate 
        suspicious activity.
        
        Find all transactions where the amount exceeds the average 
        transaction amount for that week.
        """,
        objective="Find all transactions where the amount is greater than the average transaction amount during March 10-17, 2024.",
        hint="Use a subquery to calculate the average: SELECT AVG(amount) FROM bank_transactions WHERE...",
        sql_concepts=["Subqueries", "AVG", "Nested SELECT"],
        tables_unlocked=["suspects", "phone_records", "cctv_logs", "locations", "bank_transactions"],
        expected_query="""
            SELECT * FROM bank_transactions
            WHERE amount > (
                SELECT AVG(amount) FROM bank_transactions
                WHERE timestamp BETWEEN '2024-03-10' AND '2024-03-17 23:59:59'
            )
        """,
        expected_columns=None,
        expected_row_count=6,  # Large transactions above ~5000 avg
        order_matters=False
    ),
    
    # =========================================================================
    # LEVEL 6: The Movement (CTEs)
    # =========================================================================
    6: Level(
        level_id=6,
        title="The Movement",
        story="""
        🔍 CASE FILE #2024-0315: Suspect Tracking
        
        Viktor Petrov is our prime suspect. But his lawyer, Diana Foster, 
        claims he has an alibi. She says Viktor was at his Harbor District 
        office all evening.
        
        We need to disprove this alibi by tracking Viktor's movements 
        throughout the day and night using CCTV data.
        
        Create a timeline of Viktor Petrov's (suspect ID = 3) movements 
        using CCTV sightings. This advanced analysis requires using 
        a Common Table Expression (CTE) to organize our data.
        
        Build a movement timeline to prove Viktor was NOT at his office 
        during the robbery.
        """,
        objective="Create a timeline of suspect #3's (Viktor Petrov) movements using CCTV logs. Show the timestamp and location name, ordered by time.",
        hint="Use WITH clause to create a CTE. Join cctv_logs with locations, filter by person_id = 3, then select and order.",
        sql_concepts=["WITH clause", "CTEs", "Common Table Expressions"],
        tables_unlocked=["suspects", "phone_records", "cctv_logs", "locations", "bank_transactions"],
        expected_query="""
            WITH suspect_movements AS (
                SELECT c.timestamp, l.name as location
                FROM cctv_logs c
                JOIN locations l ON c.location_id = l.id
                WHERE c.person_id = 3
            )
            SELECT * FROM suspect_movements
            ORDER BY timestamp
        """,
        expected_columns=['timestamp', 'location'],
        expected_row_count=10,  # All Viktor's CCTV sightings
        order_matters=True
    ),
    
    # =========================================================================
    # LEVEL 7: The Final Piece (Window Functions)
    # =========================================================================
    7: Level(
        level_id=7,
        title="The Final Piece",
        story="""
        🔍 CASE FILE #2024-0315: Final Evidence
        
        Detective, this is it. The final piece of the puzzle.
        
        We've tracked Viktor's movements and disproven his alibi. Now we need 
        to prove the money trail leads to him and his accomplices.
        
        Forensic accountants have flagged that criminals often have SUDDEN 
        SPIKES in their transaction amounts - unusual compared to their 
        normal patterns.
        
        Using Window Functions, analyze the transaction patterns of suspects 
        with criminal records. We need to:
        1. Rank their transactions by amount
        2. Compare each transaction to their PREVIOUS one
        3. Calculate the CHANGE in amount
        
        Find the smoking gun in the financial data!
        """,
        objective="For suspects with criminal records, analyze their transactions: show account_id, amount, timestamp, rank by amount (descending), previous amount, and the change from previous amount.",
        hint="Use RANK() OVER (PARTITION BY... ORDER BY...) and LAG() window functions. Filter using a subquery on criminal_record.",
        sql_concepts=["Window Functions", "RANK", "LAG", "PARTITION BY", "OVER"],
        tables_unlocked=["suspects", "phone_records", "cctv_logs", "locations", "bank_transactions"],
        expected_query="""
            SELECT 
                account_id,
                amount,
                timestamp,
                RANK() OVER (PARTITION BY account_id ORDER BY amount DESC) as amount_rank,
                LAG(amount) OVER (PARTITION BY account_id ORDER BY timestamp) as prev_amount,
                amount - LAG(amount) OVER (PARTITION BY account_id ORDER BY timestamp) as amount_change
            FROM bank_transactions
            WHERE account_id IN (SELECT id FROM suspects WHERE criminal_record = 1)
        """,
        expected_columns=['account_id', 'amount', 'timestamp', 'amount_rank', 'prev_amount', 'amount_change'],
        expected_row_count=8,  # Viktor (3), James (5), Natasha (10) transactions
        order_matters=False
    )
}


def get_level(level_id: int) -> Level:
    """Get a level by ID"""
    return LEVELS.get(level_id)


def get_all_levels() -> Dict[int, Level]:
    """Get all levels"""
    return LEVELS


def get_level_count() -> int:
    """Get total number of levels"""
    return len(LEVELS)


def get_tables_for_level(level_id: int) -> List[str]:
    """Get list of tables unlocked for a specific level"""
    level = get_level(level_id)
    return level.tables_unlocked if level else []
