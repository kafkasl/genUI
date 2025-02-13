document.addEventListener('DOMContentLoaded', () => {
  let rec = null, streamGlobal = null, chunks = [], btn = document.getElementById("mic-btn")
  const micIcon = document.getElementById("mic-icon")
  const stopIcon = document.getElementById("stop-icon")
  
  // Add blinking animation style
  const style = document.createElement('style')
  style.textContent = `
    @keyframes blink {
      0% { opacity: 1; }
      50% { opacity: 0.4; }
      100% { opacity: 1; }
    }
    .recording {
      animation: blink 1.5s ease-in-out infinite;
      color: #ef4444;  /* red-500 in Tailwind */
    }
  `
  document.head.appendChild(style)

  btn.addEventListener("click", async () => {
    if (!rec) {
      streamGlobal = await navigator.mediaDevices.getUserMedia({audio: true})
      rec = new MediaRecorder(streamGlobal); chunks = []
      rec.ondataavailable = e => chunks.push(e.data)
      rec.onstop = async () => {
        // Stop all audio tracks to ensure the microphone turns off
        streamGlobal.getTracks().forEach(track => track.stop())
        let blob = new Blob(chunks, {type:"audio/mp3"})
        let fd = new FormData(); fd.append("audio", blob, "recording.mp3")
        let resp = await fetch("/transcribe-voice", {method:"POST", body:fd})
        let text = await resp.text()
        let input = document.getElementById("msg-input")
        input.value = input.value ? `${input.value} ${text}` : text
        // Switch icons back
        micIcon.classList.remove('hidden')
        stopIcon.classList.add('hidden')
        rec = null; streamGlobal = null
      }
      rec.start()
      // Switch icons
      micIcon.classList.add('hidden')
      stopIcon.classList.remove('hidden')
    } else {
      rec.stop()
    }
  })
}) 