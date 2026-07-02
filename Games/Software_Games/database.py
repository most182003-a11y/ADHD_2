import sqlite3
import os
from datetime import datetime

class GameDatabase:
    def __init__(self, db_path="game_records.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the database and creates tables if they do not exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create sessions table (with new analytics columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                child_id TEXT,
                game_name TEXT,
                start_time TEXT,
                duration_minutes REAL,
                total_trials INTEGER,
                success_rate REAL,
                impulsivity_index REAL,
                motor_control_score REAL,
                distraction_score REAL,
                avg_reaction_time REAL,
                max_consecutive_success INTEGER,
                false_moves INTEGER,
                false_stops INTEGER,
                red_phase_errors INTEGER,
                green_phase_errors INTEGER,
                average_similarity REAL DEFAULT 0.0,
                total_fidget_score REAL DEFAULT 0.0,
                attention_overall REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create rounds/trials table (with detailed per-trial analytics)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                child_id TEXT,
                game_name TEXT,
                movement TEXT,
                target_pose_id TEXT DEFAULT '',
                reaction_time REAL,
                success INTEGER,
                hold_duration REAL,
                direction_error INTEGER,
                stability REAL,
                is_premature INTEGER,
                pose_similarity REAL DEFAULT 0.0,
                fidget_score REAL DEFAULT 0.0,
                attention_percent REAL DEFAULT 1.0,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)

        conn.commit()

        # --- Migration: add columns if upgrading from old schema ---
        self._migrate_add_column(cursor, "sessions", "average_similarity", "REAL DEFAULT 0.0")
        self._migrate_add_column(cursor, "sessions", "total_fidget_score", "REAL DEFAULT 0.0")
        self._migrate_add_column(cursor, "sessions", "attention_overall", "REAL DEFAULT 1.0")
        self._migrate_add_column(cursor, "rounds", "target_pose_id", "TEXT DEFAULT ''")
        self._migrate_add_column(cursor, "rounds", "pose_similarity", "REAL DEFAULT 0.0")
        self._migrate_add_column(cursor, "rounds", "fidget_score", "REAL DEFAULT 0.0")
        self._migrate_add_column(cursor, "rounds", "attention_percent", "REAL DEFAULT 1.0")
        conn.commit()
        conn.close()

    def _migrate_add_column(self, cursor, table, column, col_def):
        """Safely adds a column if it does not exist."""
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
        except sqlite3.OperationalError:
            pass  # Column already exists

    def save_round(self, session_id, child_id, game_name, movement, reaction_time, success, hold_duration, direction_error, stability=0.0, is_premature=0, target_pose_id="", pose_similarity=0.0, fidget_score=0.0, attention_percent=1.0):
        """Saves data for a single round of a game with detailed analytics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO rounds (
                session_id, child_id, game_name, movement, target_pose_id,
                reaction_time, success, hold_duration, direction_error,
                stability, is_premature, pose_similarity, fidget_score,
                attention_percent, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, child_id, game_name, movement, target_pose_id,
            reaction_time, success, hold_duration, direction_error,
            stability, is_premature, pose_similarity, fidget_score,
            attention_percent, timestamp
        ))
        
        conn.commit()
        conn.close()
        print(f"[DB] Saved round: {movement} | Success: {success} | React: {reaction_time}s | Sim: {pose_similarity:.2f}")

    def save_session(self, session_summary, sync_remote=True):
        """Saves a summary of a completed game session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (
                session_id, child_id, game_name, start_time, duration_minutes, total_trials, success_rate, 
                impulsivity_index, motor_control_score, distraction_score, avg_reaction_time, 
                max_consecutive_success, false_moves, false_stops, red_phase_errors, green_phase_errors,
                average_similarity, total_fidget_score, attention_overall
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_summary.get("session_id"),
            session_summary.get("child_id"),
            session_summary.get("game_name"),
            session_summary.get("start_time"),
            session_summary.get("duration_minutes"),
            session_summary.get("total_trials"),
            session_summary.get("success_rate"),
            session_summary.get("impulsivity_index"),
            session_summary.get("motor_control_score"),
            session_summary.get("distraction_score"),
            session_summary.get("avg_reaction_time"),
            session_summary.get("max_consecutive_success"),
            session_summary.get("false_moves"),
            session_summary.get("false_stops"),
            session_summary.get("red_phase_errors"),
            session_summary.get("green_phase_errors"),
            session_summary.get("average_similarity", 0.0),
            session_summary.get("total_fidget_score", 0.0),
            session_summary.get("attention_overall", 1.0)
        ))
        
        conn.commit()
        conn.close()
        print(f"[DB] Saved session summary locally: {session_summary.get('session_id')} | Success Rate: {session_summary.get('success_rate')}%")
        
        # Synchronize with C# Backend API (skip if caller handles sync separately)
        if sync_remote:
            self.sync_to_backend(session_summary)

    def get_trials(self, session_id):
        """Retrieves all trials for a given session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rounds WHERE session_id = ? ORDER BY id", (session_id,))
        rows = cursor.fetchall()
        conn.close()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def sync_to_backend(self, session_summary):
        """Sends session summary data to the .NET Web API backend."""
        try:
            import requests
            
            child_id = session_summary.get("child_id")
            # If default offline id is used, skip syncing to backend
            if not child_id or child_id == "CHILD001":
                print("[API Sync] Default offline child ID detected. Skipping backend sync.")
                return False
                
            raw_difficulty = session_summary.get("difficulty", "Medium")
            if not isinstance(raw_difficulty, int):
                raw_diff_str = str(raw_difficulty).lower()
                if "easy" in raw_diff_str:
                    difficulty = 0
                elif "hard" in raw_diff_str:
                    difficulty = 2
                else:
                    difficulty = 1
            else:
                difficulty = raw_difficulty

            # Raw values
            success_rate = float(session_summary.get("success_rate", 0.0))
            impulsivity = float(session_summary.get("impulsivity_index", 0.0))
            motor_control = float(session_summary.get("motor_control_score", 0.0))
            distraction = float(session_summary.get("distraction_score", 0.0))
            avg_reaction = float(session_summary.get("avg_reaction_time", 0.0))
            
            # Normalize to 0.0 - 1.0 range if they are stored as percentages (0 - 100)
            if impulsivity > 1.0:
                impulsivity = impulsivity / 100.0
            if motor_control > 1.0:
                motor_control = motor_control / 100.0
            if distraction > 1.0:
                distraction = distraction / 100.0
                
            # Convert reaction time from seconds to milliseconds
            avg_reaction_ms = avg_reaction * 1000.0 if avg_reaction < 10.0 else avg_reaction
            
            # Composite score calculation (based on C# domain guidelines)
            player_score = (success_rate * 0.5) + ((1.0 - impulsivity) * 30.0) + (motor_control * 20.0)
            player_score = round(min(max(player_score, 0.0), 100.0), 2)
            
            game_name = session_summary.get("game_name", "")
            game_id = None
            api_base_url = os.getenv("ADHD_API_BASE_URL", "http://localhost:5131/api").rstrip("/")
            device_api_key = os.getenv("GAME_DEVICE_API_KEY", "dev-game-device-key-change-me")
            
            # Fetch games dynamically from C# Backend first for maximum robustness
            try:
                games_url = f"{api_base_url}/games"
                games_res = requests.get(games_url, timeout=3)
                if games_res.status_code == 200:
                    games_data = games_res.json().get("data", [])
                    db_games = {g["name"].lower(): g["id"] for g in games_data}
                    
                    if "green" in game_name.lower() or "الضوء" in game_name:
                        game_id = db_games.get("green light")
                    elif "mirror" in game_name.lower() or "انعكاس" in game_name:
                        game_id = db_games.get("mirror me")
                    elif "simon" in game_name.lower() or "سايمون" in game_name:
                        game_id = db_games.get("simon game")
                    elif "reaction" in game_name.lower() or "الاستجابة" in game_name:
                        game_id = db_games.get("light reaction")
                    
                    if game_id:
                        print(f"[API Sync] Dynamically resolved game ID from backend: {game_id}")
            except Exception as ex:
                print(f"[API Sync] Warning: Could not dynamically resolve game IDs from backend: {ex}. Using static fallbacks.")
                
            # If dynamic resolution failed or was empty, use static seeded fallbacks
            if not game_id:
                if "green" in game_name.lower() or "الضوء" in game_name:
                    game_id = "cfefe7e7-f858-4d27-8dba-b356f35de22c"  # Green Light
                elif "mirror" in game_name.lower() or "انعكاس" in game_name:
                    game_id = "06bc62cb-4d0c-4f74-b3a3-e569bd4163ad"  # Mirror Me
                elif "simon" in game_name.lower() or "سايمون" in game_name:
                    game_id = "54bd242c-6a43-4d99-866e-74809e8c5201"  # Simon Game
                elif "reaction" in game_name.lower() or "الاستجابة" in game_name:
                    game_id = "7dce4e9e-d20b-40a7-a2d5-6e3c9f0cda5e"  # Light Reaction
            
            avg_similarity = float(session_summary.get("average_similarity", 0.0))
            total_fidget = float(session_summary.get("total_fidget_score", 0.0))
            attention = float(session_summary.get("attention_overall", 1.0))

            payload = {
                "childId": child_id,
                "gameId": game_id,
                "startTime": session_summary.get("start_time"),
                "durationMinutes": int(round(float(session_summary.get("duration_minutes", 0.0)))),
                "difficultyLevel": difficulty,
                "totalTrials": int(session_summary.get("total_trials", 0)),
                "successRate": round(success_rate, 2),
                "playerScore": player_score,
                "impulsivityIndex": round(impulsivity, 2),
                "motorControlScore": round(motor_control, 2),
                "falseMoves": int(session_summary.get("false_moves", 0)),
                "distractionScore": round(distraction, 2),
                "avgReactionTime": round(avg_reaction_ms, 2),
                "falseStops": int(session_summary.get("false_stops", 0)),
                "maxConsecutiveSuccess": int(session_summary.get("max_consecutive_success", 0)),
                "averageSimilarity": round(avg_similarity, 2),
                "totalFidgetScore": round(total_fidget, 2),
                "attentionOverall": round(attention, 2)
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Game-Device-Key": device_api_key
            }
            url = f"{api_base_url}/sessions"
            print(f"[API Sync] Sending session payload to {url}...")
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"[API Sync] Successfully synced session to C# backend! Status: {response.status_code}")
                return True
            else:
                print(f"[API Sync] Failed to sync session to backend. Status: {response.status_code}, Response: {response.text}")
                return False
        except ImportError:
            print("[API Sync] 'requests' library not found. Skipping backend sync.")
            return False
        except Exception as e:
            print(f"[API Sync] Network/Server Error during backend sync: {e}. Session saved locally only.")
            return False
