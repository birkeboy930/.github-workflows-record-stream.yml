#!/usr/bin/env python3
import subprocess
import os
import datetime

def main():
    # Skapa recordings mapp om den inte finns
    os.makedirs('recordings', exist_ok=True)
    
    # Tidsstämpel för filnamn
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'recordings/eu_stream_{timestamp}.mp3'
    
    # EU Stream URL
    stream_url = os.environ.get('STREAM_URL', 'https://audiovisual.ec.europa.eu/en/ebs/live/2')
    
    print(f"Startar inspelning från: {stream_url}")
    print(f"Sparar till: {output_file}")
    print("Inspelning pågår i 5 minuter...")
    
    # FFmpeg kommando för 5 minuters inspelning
    cmd = [
        'ffmpeg',
        '-i', stream_url,
        '-t', '300',  # 300 sekunder = 5 minuter
        '-acodec', 'mp3',
        '-ab', '128k',
        '-y',  # Skriv över befintliga filer
        output_file
    ]
    
    try:
        # Kör FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=400)
        
        if result.returncode == 0:
            print("Inspelning slutförd!")
            print(f"Fil sparad: {output_file}")
            
            # Kontrollera filstorlek
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"Filstorlek: {size / 1024 / 1024:.2f} MB")
            else:
                print("VARNING: Fil hittades inte!")
                
        else:
            print("FEL vid inspelning:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("Timeout - inspelning avbruten")
    except Exception as e:
        print(f"Fel uppstod: {e}")

if __name__ == "__main__":
    main()
