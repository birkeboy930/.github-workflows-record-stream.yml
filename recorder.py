#!/usr/bin/env python3
import subprocess
import os
import datetime
import time

def test_stream_url(url, timeout=10):
    """Testa om en stream-URL fungerar"""
    print(f"Testar stream: {url}")
    cmd = [
        'ffmpeg',
        '-i', url,
        '-t', '1',  # Bara 1 sekund för test
        '-f', 'null',
        '-'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"✅ Stream fungerar: {url}")
            return True
        else:
            print(f"❌ Stream fungerar inte: {url}")
            print(f"Fel: {result.stderr[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout för: {url}")
        return False
    except Exception as e:
        print(f"🚫 Fel vid test av {url}: {e}")
        return False

def record_stream(url, output_file, duration=300):
    """Spela in från stream"""
    print(f"Startar inspelning från: {url}")
    print(f"Sparar till: {output_file}")
    print(f"Inspelning pågår i {duration//60} minuter...")
    
    # FFmpeg kommando med robusta inställningar
    cmd = [
        'ffmpeg',
        '-y',  # Skriv över befintliga filer
        '-headers', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        '-i', url,
        '-t', str(duration),
        '-acodec', 'mp3',
        '-ab', '128k',
        '-ar', '44100',  # Sample rate
        '-ac', '2',      # Stereo
        '-avoid_negative_ts', 'make_zero',
        '-fflags', '+genpts',
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration+60)
        
        if result.returncode == 0:
            print("✅ Inspelning slutförd!")
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"📁 Filstorlek: {size / 1024 / 1024:.2f} MB")
                return True
            else:
                print("❌ Fil skapades inte!")
                return False
        else:
            print("❌ FFmpeg fel:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Inspelning timeout")
        return False
    except Exception as e:
        print(f"🚫 Fel vid inspelning: {e}")
        return False

def main():
    # Skapa recordings mapp
    os.makedirs('recordings', exist_ok=True)
    
    # Tidsstämpel för filnamn
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Lista över stream-URLer att testa (i prioritetsordning)
    stream_urls = [
        # EU Officiella streams
        'https://audiovisual.ec.europa.eu/en/ebs/live/2',
        'https://europarltv.europa.eu/en/programme/live',
        'https://multimedia.europarl.europa.eu/en/webstreaming/press-conference',
        
        # EU Radio streams (mer sannolika att fungera)
        'https://euradio.eu/stream',
        'https://live.euradio.eu/euradio.mp3',
        
        # Backup: Välkända europeiska radio-streams
        'https://stream.srg-ssr.ch/rsp/aacp_48.m3u8',
        'https://icecast.omroep.nl/radio1-bb-mp3',
        'https://dispatcher.rndfnk.com/br/br2/live/mp3/low',
        
        # Last resort: BBC World Service (engelska)
        'https://stream.live.vc.bbcmedia.co.uk/bbc_world_service',
        'https://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_world_service.m3u8'
    ]
    
    successful_url = None
    
    print("🔍 Söker efter fungerande stream...")
    
    # Testa varje URL tills vi hittar en som fungerar
    for url in stream_urls:
        if test_stream_url(url):
            successful_url = url
            break
        time.sleep(2)  # Vänta mellan test
    
    if not successful_url:
        print("❌ Ingen fungerande stream hittades!")
        print("🔄 Försöker med enklare approach...")
        
        # Fallback: Testa utan headers
        for url in stream_urls[:3]:  # Bara EU-streams
            print(f"Försöker utan headers: {url}")
            simple_cmd = ['ffmpeg', '-i', url, '-t', '1', '-f', 'null', '-']
            try:
                result = subprocess.run(simple_cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    successful_url = url
                    print(f"✅ Fungerar utan headers: {url}")
                    break
            except:
                continue
    
    if not successful_url:
        print("💔 Alla streams misslyckades. Skapar test-fil...")
        # Skapa en tom testfil så något ladda upp
        test_file = f'recordings/no_stream_found_{timestamp}.txt'
        with open(test_file, 'w') as f:
            f.write(f"Ingen fungerande stream hittades vid {datetime.datetime.now()}\n")
            f.write("Testade URLs:\n")
            for url in stream_urls:
                f.write(f"- {url}\n")
        print(f"📝 Test-fil skapad: {test_file}")
        return
    
    # Spela in från fungerande stream
    output_file = f'recordings/eu_stream_{timestamp}.mp3'
    
    print(f"🎯 Använder stream: {successful_url}")
    success = record_stream(successful_url, output_file)
    
    if success:
        print("🎉 Inspelning lyckades!")
    else:
        print("😞 Inspelning misslyckades")
        # Skapa info-fil ändå
        info_file = f'recordings/failed_recording_{timestamp}.txt'
        with open(info_file, 'w') as f:
            f.write(f"Inspelning misslyckades vid {datetime.datetime.now()}\n")
            f.write(f"Använda URL: {successful_url}\n")

if __name__ == "__main__":
    main()
