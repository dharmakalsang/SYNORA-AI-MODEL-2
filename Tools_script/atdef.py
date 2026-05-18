# --------------------------------------------------------------
# REMINDER THIS IS IF SOMEONE FOR SOME REASON
# WANTS TO SEE THE CODE, THIS IS NOT THE MAIN FILE
# INCLUDING NOT SAFE FOR HURTABLE USES
# --------------------------------------------------------------
# --------------------------------------------------------------
# USE IF SOMEONE ATTACK YOU FIRST THIS IS A WARNING
# AND 
# FULL PROTOTYPE ATTACKER 
# --------------------------------------------------------------
# --------------------------------------------------------------
print ("===========================================================")
print ("This is a prototype, not the main file. Use with caution.")
print ("===========================================================")

print ("HELLO THERE :D")




question  = input("DO YOU LIKE TO BE HACKED?(yes/no): ")
question = input("ARE YOU SURE?(yes/no): ")
question = input("ARE YOU REALLY SURE?(yes/no): ")  
question = input("ARE YOU REALLY REALLY SURE?(yes/no): ")
question = input("ARE YOU REALLY REALLY REALLY SURE?(yes/no): ")      
print ("Alright, you have been warned.")

import time
import random
import sys

# Fake file names to "destroy"
fake_files = [
    "system32.dll",
    "bootmgr.exe",
    "ntoskrnl.sys",
    "config.sys",
    "master_boot.rec",
    "korben_dallas_data.mem",
    "classified.project_x",
    "backup_2025.zip",
    "password_store.bin",
    "the_plan.pdf",
    "secret_recipes.doc",
    "tax_evasion_notes.txt",
    "old_photos",  # folder
    "windows.old",
    "pagefile.sys",
]

# Destructive verbs/phrases
destroy_phrases = [
    "DELETING",
    "SHREDDING",
    "CORRUPTING",
    "PURGING",
    "ERADICATING",
    "DESTROYING",
    "OBLITERATING",
    "WIPING",
    "SCRAMBLING",
    "VAPORIZING",
]

def simulate_destruction(duration=8, files_per_second=1.5):
    """
    Simulate a "destroying files" loading effect.
    
    Args:
        duration: How long the effect runs (seconds)
        files_per_second: How many fake files to "destroy" per second
    """
    total_files = int(duration * files_per_second)
    # Randomly pick files (allow repeats)
    files_to_destroy = [random.choice(fake_files) for _ in range(total_files)]
    
    print("\n" + "=" * 50)
    print("💀  INITIATING FILE DESTRUCTION SEQUENCE  💀")
    print("=" * 50 + "\n")
    
    start_time = time.time()
    destroyed_count = 0
    
    try:
        for file in files_to_destroy:
            # Calculate elapsed time and progress
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
                
            # Random destruction style
            action = random.choice(destroy_phrases)
            # Optional: extra "effect" characters
            sparkles = random.choice(["⚡", "💥", "🔥", "💣", "🗑️", "💀"])
            
            # Simulate "processing" with a little bar animation
            sys.stdout.write(f"\r{action} [{file:25}] ")
            sys.stdout.flush()
            
            # Fake "hard drive grinding" delay (varies per file)
            processing_time = random.uniform(0.1, 0.4)
            time.sleep(processing_time)
            
            # Overwrite line with destroyed confirmation
            print(f"\r{sparkles} DESTROYED: {file:<30} {sparkles}")
            
            destroyed_count += 1
            
            # Random dramatic pause between files (makes it feel more real)
            time.sleep(random.uniform(0.1, 0.3))
        
        # Progress bar that fills while "deleting" (optional extra)
        print("\n")
        bar_length = 40
        for i in range(bar_length + 1):
            percent = (i / bar_length) * 100
            bar = "█" * i + "░" * (bar_length - i)
            sys.stdout.write(f"\r🗑️  PERMANENT DAMAGE: |{bar}| {percent:.1f}%")
            sys.stdout.flush()
            time.sleep(0.03)
        
        print("\n\n" + "=" * 50)
        print(f"✅ {destroyed_count} files have been DESTROYED beyond recovery.")
        print("💀 System memory corrupted. Please insert anti-virus. 💀")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  DESTRUCTION HALTED. Files may be partially recoverable. ⚠️")
        sys.exit(0)

if __name__ == "__main__":
    simulate_destruction(duration=8, files_per_second=1.8)
    
    import os
import platform
import subprocess

def shutdown_now():
    system = platform.system()
    if system == "Windows":
        subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
    elif system == "Linux" or system == "Darwin":
        subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

if __name__ == "__main__":
    shutdown_now()