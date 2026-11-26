import React, { useState, useRef, useEffect, useCallback } from 'react'
import { aiService } from '../../services/aiService'
import { useThemeStore } from '../../store/useThemeStore'
import type { ChatMessage } from '../../types/ai'
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Square,
  Sparkles,
  Send,
  X,
  AlertCircle
} from 'lucide-react'
import { Badge } from '../ui'

interface VoiceAssistantWidgetProps {
  attemptId: string | null
  experimentTitle: string
  experimentSlug?: string
  currentStepIndex: number
  lastErrorCode: string | null
  lastActionSummary?: string
  className?: string
}

// پرسش‌های صوتی سریع بر اساس آزمایش‌های مصوب کتاب درسی
const EXPERIMENT_VOICE_PROMPTS: Record<string, string[]> = {
  'acid-base-indicators': [
    'چرا کاغذ تورنسل در آب‌لیمو سرخ شد؟',
    'آب‌صابون چه خصلتی دارد و چه اثری بر شناساگر می‌گذارد؟',
    'کاغذ تورنسل در آب‌مقطر چرا تغییر رنگ نداد؟',
    'تفاوت شناساگرهای طبیعی با تورنسل و فنل‌فتالئین چیست؟'
  ],
  'vinegar-baking-soda-reaction': [
    'گاز خروجی از واکنش سرکه و جوش‌شیرین چیست؟',
    'چرا بعد از مدتی جوشش متوقف می‌شود؟',
    'چرا ظرف آزمایش هنگام واکنش سرد می‌شود؟',
    'معادله واکنش بین جوش‌شیرین و سرکه چیست؟'
  ],
  'simple-pendulum-motion': [
    'آیا تغییر جرم وزنه در زمان نوسان آونگ اثر دارد؟',
    'چرا نباید زاویه رهاسازی بیشتر از ۱۵ درجه باشد؟',
    'برای اینکه زمان تناوب دو برابر شود، طول نخ باید چقدر شود؟',
    'فرمول دوره تناوب آونگ ساده چیست؟'
  ],
  'plant-water-transport-celery': [
    'آب رنگی از چه بافتی در ساقه بالا رفته است؟',
    'نقش تبخیر سطحی از روزنه‌های برگ در صعود آب چیست؟',
    'تفاوت آوند چوبی با آوند آبکشی چیست؟',
    'چرا فقط دسته‌های آوندی به رنگ جوهر درآمدند؟'
  ],
  'liquid-density-column': [
    'چرا روغن روی سطح آب معلق می‌ماند؟',
    'آیا مایع سنگین‌تر حتماً در پایین‌ترین لایه قرار می‌گیرد؟',
    'تفاوت جرم، حجم و چگالی مایعات در این آزمایش چیست؟',
    'چرا مایعات لایه‌بندی‌شده سریع در هم مخلوط نمی‌شوند؟'
  ],
  'water-filtration-column': [
    'آیا آب زلال خروجی از صافی قابل شرب است؟',
    'چرا ترتیب لایه‌ها از درشت به ریز (شن، ماسه، کربن) است؟',
    'آیا این صافی نمک محلول را هم جدا می‌کند؟',
    'کربن فعال چه نقشی در پالایش آب دارد؟'
  ],
  'mixture-separation-sand-salt': [
    'چرا ماسه در آب حل نشد ولی نمک کاملاً حل شد؟',
    'چرا ابتدا باید صاف کنیم و بعد حرارت دهیم؟',
    'نقطه جوش آب و نمک چه کمکی به جداسازی آن‌ها می‌کند؟',
    'چرا در انتهای تبخیر باید حرارت را ملایم یا قطع کنیم؟'
  ],
  'simple-electric-circuit-ohm': [
    'چرا لامپ در مدار باز روشن نمی‌شود؟',
    'خطر اتصال کوتاه در مدار چیست و چه آسیبی می‌زند؟',
    'بر اساس قانون اهم، اگر مقاومت زیاد شود جریان چه می‌شود؟',
    'آمپرمتر و ولت‌سنج چگونه در مدار بسته می‌شوند؟'
  ]
}

const DEFAULT_VOICE_PROMPTS = [
  'هدف اصلی این آزمایش علمی چیست؟',
  'در این گام چه ابزارهایی را باید استفاده کنم؟',
  'دلیل رخ دادن خطای جاری چیست؟',
  'قانون علمی حاکم بر این مرحله را صوتی توضیح بده.'
]

export const VoiceAssistantWidget: React.FC<VoiceAssistantWidgetProps> = ({
  attemptId,
  experimentTitle,
  experimentSlug,
  currentStepIndex,
  lastErrorCode,
  lastActionSummary,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [liveTranscript, setLiveTranscript] = useState('')
  const [questionInput, setQuestionInput] = useState('')
  const [autoSpeakEnabled, setAutoSpeakEnabled] = useState(true)
  const [selectedVoice, setSelectedVoice] = useState<'fa-IR-DilaraNeural' | 'fa-IR-FaridNeural'>('fa-IR-DilaraNeural')
  const [hasVoiceError, setHasVoiceError] = useState(false)
  const [voiceErrorMessage, setVoiceErrorMessage] = useState('')
  const [hasNewErrorAlert, setHasNewErrorAlert] = useState(false)
  const { theme } = useThemeStore()
  const isLight = theme === 'light'

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'voice-welcome',
      sender: 'ai',
      text: `سلام! من دستیار صوتی هوشمند آزمایشگاه هستم. می‌توانید دکمه میکروفون را بزنید و سوالات علمی یا راهنمایی مراحل آزمایش «${experimentTitle}» را به زبان فارسی از من بپرسید!`,
      timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })
    }
  ])

  const audioPlayerRef = useRef<HTMLAudioElement | null>(null)
  const recognitionRef = useRef<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const transcriptBufferRef = useRef<string>('')
  const silenceTimerRef = useRef<any>(null)

  // به‌روزرسانی پیام خوش‌آمدگویی هنگام تغییر آزمایش
  useEffect(() => {
    setMessages([
      {
        id: 'voice-welcome',
        sender: 'ai',
        text: `سلام! من دستیار صوتی هوشمند آزمایشگاه هستم. می‌توانید دکمه میکروفون را بزنید و سوالات علمی یا راهنمایی مراحل آزمایش «${experimentTitle}» را به زبان فارسی از من بپرسید!`,
        timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })
      }
    ])
  }, [experimentTitle, experimentSlug])

  // اسکرول نرم پیام‌ها به پایین
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isProcessing, liveTranscript])

  // آگاه‌سازی صوتی هنگام رخداد خطا در آزمایش
  useEffect(() => {
    if (lastErrorCode) {
      setHasNewErrorAlert(true)
    }
  }, [lastErrorCode])

  // تشخیص پرسش‌های صوتی پیشنهادی برای آزمایش فعال
  const voicePrompts =
    (experimentSlug && EXPERIMENT_VOICE_PROMPTS[experimentSlug]) ||
    EXPERIMENT_VOICE_PROMPTS[
      Object.keys(EXPERIMENT_VOICE_PROMPTS).find((slug) =>
        experimentTitle.includes(slug) ||
        (slug === 'acid-base-indicators' && experimentTitle.includes('اسید')) ||
        (slug === 'vinegar-baking-soda-reaction' && experimentTitle.includes('سرکه')) ||
        (slug === 'simple-pendulum-motion' && experimentTitle.includes('آونگ')) ||
        (slug === 'plant-water-transport-celery' && experimentTitle.includes('کرفس')) ||
        (slug === 'liquid-density-column' && experimentTitle.includes('چگالی')) ||
        (slug === 'water-filtration-column' && experimentTitle.includes('صافی')) ||
        (slug === 'mixture-separation-sand-salt' && experimentTitle.includes('ماسه')) ||
        (slug === 'simple-electric-circuit-ohm' && experimentTitle.includes('مدار'))
      ) || ''
    ] ||
    DEFAULT_VOICE_PROMPTS

  // توقف پخش صوت جاری
  const stopAudio = useCallback(() => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause()
      audioPlayerRef.current.currentTime = 0
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
    setIsSpeaking(false)
  }, [])

  // خواندن متن با صوت فارسی (Edge-TTS سرور با فال‌بک SpeechSynthesis مرورگر)
  const speakText = useCallback(async (textToSpeak: string) => {
    if (!textToSpeak.trim()) return
    stopAudio()
    setIsSpeaking(true)

    // پاک‌سازی علائم نگارشی اضافه برای گویش روان‌تر
    const cleanText = textToSpeak
      .replace(/[#*`_~]/g, '')
      .replace(/[\n\r]+/g, '، ')
      .trim()

    try {
      // تلاش اول: درخواست صوت استودیویی و طبیعی از سرور با Edge-TTS
      const audioBlob = await aiService.getVoiceTTSAudio(cleanText, selectedVoice)
      const audioUrl = URL.createObjectURL(audioBlob)

      const audio = new Audio(audioUrl)
      audioPlayerRef.current = audio

      audio.onended = () => {
        setIsSpeaking(false)
        URL.revokeObjectURL(audioUrl)
      }

      audio.onerror = () => {
        // اگر اجرای فایل دانلودی با مشکل مواجه شد، به سنتز مرورگر سوئیچ می‌کنیم
        fallbackBrowserTTS(cleanText)
      }

      await audio.play()
    } catch (err) {
      // فال‌بک مطمئن و آفلاین: استفاده از SpeechSynthesis محلی مرورگر
      fallbackBrowserTTS(cleanText)
    }
  }, [selectedVoice, stopAudio])

  const fallbackBrowserTTS = (text: string) => {
    if (!('speechSynthesis' in window)) {
      setIsSpeaking(false)
      return
    }

    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'fa-IR'
    utterance.rate = 0.95

    const voices = window.speechSynthesis.getVoices()
    const faVoice = voices.find(v => v.lang.includes('fa') || v.lang.includes('fa-IR'))
    if (faVoice) {
      utterance.voice = faVoice
    }

    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }

  // راه‌اندازی و اجرای تشخیص گفتار فارسی (Web Speech API)
  const startListening = () => {
    stopAudio()
    setHasVoiceError(false)
    setVoiceErrorMessage('')
    setLiveTranscript('')
    transcriptBufferRef.current = ''

    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      setHasVoiceError(true)
      setVoiceErrorMessage('مرورگر شما از تشخیص گفتار پشتیبانی نمی‌کند. لطفاً از مرورگر Chrome یا Edge استفاده نمایید یا متن را تایپ کنید.')
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognition.lang = 'fa-IR'
      recognition.continuous = false
      recognition.interimResults = true

      recognition.onstart = () => {
        setIsListening(true)
        setLiveTranscript('')
        transcriptBufferRef.current = ''
      }

      recognition.onresult = (event: any) => {
        let accumulated = ''
        for (let i = 0; i < event.results.length; i++) {
          accumulated += event.results[i][0].transcript + ' '
        }
        const clean = accumulated.trim()
        if (clean) {
          setLiveTranscript(clean)
          setQuestionInput(clean)
          transcriptBufferRef.current = clean
        }
      }

      recognition.onerror = (event: any) => {
        setIsListening(false)
        if (event.error === 'network') {
          setHasVoiceError(true)
          setVoiceErrorMessage('⚠️ سرور تبدیل گفتار مرورگر (گوگل) مسدود است یا نیاز به اتصال اینترنت پایدار دارد. لطفاً سوال را در کادر زیر تایپ فرمایید.')
        } else if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          setHasVoiceError(true)
          setVoiceErrorMessage('⚠️ دسترسی به میکروفون مسدود است. لطفاً از آیکون قفل کنار نوار آدرس مرورگر دسترسی میکروفون را فعال (Allow) کنید.')
        } else if (event.error === 'no-speech') {
          setHasVoiceError(true)
          setVoiceErrorMessage('⚠️ صدایی دریافت نشد. لطفاً بلندتر و نزدیک به میکروفون صحبت کنید یا سوال را تایپ نمایید.')
        } else {
          setHasVoiceError(true)
          setVoiceErrorMessage(`⚠️ خطای میکروفون (${event.error}). لطفاً سوال را تایپ نمایید.`)
        }
      }

      recognition.onend = () => {
        setIsListening(false)
        const text = transcriptBufferRef.current.trim()
        if (text && text.length >= 2) {
          handleSendVoiceQuestion(text)
          transcriptBufferRef.current = ''
        }
      }

      recognitionRef.current = recognition
      recognition.start()
    } catch (err) {
      setIsListening(false)
      setHasVoiceError(true)
      setVoiceErrorMessage('امکان راه‌اندازی ضبط صوت وجود ندارد.')
    }
  }

  const stopListening = () => {
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current)
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch {}
    }
    setIsListening(false)
    const text = transcriptBufferRef.current.trim()
    if (text && text.length >= 2) {
      handleSendVoiceQuestion(text)
      transcriptBufferRef.current = ''
    }
  }

  // ارسال پرسش صوتی یا متنی به سرور و دریافت پاسخ
  const handleSendVoiceQuestion = async (text: string) => {
    const questionText = text.trim()
    if (!questionText || !attemptId || isProcessing) return

    stopAudio()
    setLiveTranscript('')
    setQuestionInput('')

    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: questionText,
      timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })
    }

    setMessages((prev) => [...prev, userMsg])
    setIsProcessing(true)

    try {
      const res = await aiService.askAITutorQuestion(
        attemptId,
        questionText,
        currentStepIndex
      )

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        text: res.answer,
        isAiGenerated: res.is_ai_generated,
        timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })
      }

      setMessages((prev) => [...prev, aiMsg])

      // اگر پخش خودکار فعال باشد، پاسخ بلافاصله با صوت خوانده می‌شود
      if (autoSpeakEnabled) {
        speakText(res.answer)
      }
    } catch (err) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'ai',
        text: 'متأسفانه در پاسخ‌گویی مشکلی پیش آمد. لطفاً پرسش خود را دوباره تکرار فرمایید.',
        timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsProcessing(false)
    }
  }

  // درخواست توضیح صوتی خطای رخ‌داده در آزمایش
  const handleVoiceErrorExplanation = async () => {
    if (!attemptId || !lastErrorCode) return
    setIsProcessing(true)
    setHasNewErrorAlert(false)

    try {
      const res = await aiService.requestAITutorHint(
        attemptId,
        lastErrorCode,
        currentStepIndex,
        lastActionSummary,
        2 // سرنخ علمی پداگوژیک
      )

      const explanationText = `در این مرحله: ${res.content}. مفهوم علمی مرتبط: ${res.scientific_rationale || 'اصول کتاب درسی'}`

      const aiMsg: ChatMessage = {
        id: `hint-voice-${Date.now()}`,
        sender: 'ai',
        text: explanationText,
        isAiGenerated: res.is_ai_generated,
        timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })
      }

      setMessages((prev) => [...prev, aiMsg])

      if (autoSpeakEnabled) {
        speakText(explanationText)
      }
    } catch (err) {
      console.error('خطا در دریافت راهنمای صوتی:', err)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <aside aria-label="دستیار صوتی هوشمند آزمایشگاه" className={`relative z-40 ${className}`}>
      {/* دکمه شناور باز کردن دستیار صوتی */}
      {!isOpen && (
        <button
          onClick={() => {
            setIsOpen(true)
            setHasNewErrorAlert(false)
          }}
          className={`fixed bottom-6 left-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-full shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300 border group ${
            isLight
              ? 'bg-gradient-to-r from-emerald-600 via-teal-600 to-sky-600 text-white border-emerald-300/60 shadow-emerald-600/30'
              : 'bg-gradient-to-r from-teal-500 via-emerald-600 to-indigo-700 text-white border-emerald-300/40 hover:shadow-emerald-500/40'
          }`}
          title="دستیار صوتی هوشمند آزمایشگاه"
        >
          <div className="relative flex items-center justify-center">
            <Mic className="w-5 h-5 text-amber-300 animate-bounce group-hover:scale-110 transition-transform" />
            {hasNewErrorAlert && (
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-rose-500 rounded-full border-2 border-white animate-ping" />
            )}
          </div>
          <span className="text-sm font-bold tracking-wide">معلم‌یار صوتی آزمایشگاه</span>
          {isSpeaking && (
            <span className="flex items-center gap-1 bg-amber-400 text-slate-950 text-xs px-2 py-0.5 rounded-full font-bold animate-pulse">
              <Volume2 className="w-3.5 h-3.5" />
              در حال صحبت
            </span>
          )}
          {hasNewErrorAlert && (
            <span className="bg-rose-500 text-white text-xs px-2.5 py-0.5 rounded-full font-bold">
              راهنمای صوتی خطا
            </span>
          )}
        </button>
      )}

      {/* پنل دستیار صوتی هوشمند */}
      {isOpen && (
        <div className={`fixed bottom-6 left-6 z-50 w-96 sm:w-[440px] h-[600px] max-h-[85vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden text-right font-sans animate-in fade-in zoom-in-95 duration-200 border ${
          isLight
            ? 'bg-white/95 backdrop-blur-xl border-emerald-200 text-slate-800 shadow-slate-300/60'
            : 'bg-slate-900/95 backdrop-blur-xl border-emerald-500/30 text-white'
        }`}>
          
          {/* هدر پنل صوتی */}
          <div className={`px-4 py-3.5 border-b flex items-center justify-between ${
            isLight
              ? 'bg-gradient-to-r from-emerald-50 via-teal-50 to-sky-50 border-emerald-200/80 text-emerald-950'
              : 'bg-gradient-to-r from-emerald-950 via-slate-900 to-indigo-950 border-emerald-500/20 text-white'
          }`}>
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-slate-950 shadow-md shadow-emerald-500/20">
                <Mic className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className={`text-sm font-black ${isLight ? 'text-emerald-950' : 'text-white'}`}>معلم‌یار صوتی آزمایشگاه</h3>
                  <Badge variant="emerald" className="text-[10px] px-1.5 py-0 font-bold">گفتار زنده</Badge>
                </div>
                <p className={`text-[11px] ${isLight ? 'text-emerald-700' : 'text-emerald-300/80'}`}>پشتیبانی از صوت فارسی طبیعی (بدون نیاز به API)</p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              {/* تنظیم گوینده */}
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value as any)}
                className={`text-xs rounded-xl px-2.5 py-1 border outline-none font-medium transition-colors ${
                  isLight
                    ? 'bg-white text-emerald-900 border-emerald-300 hover:bg-emerald-50'
                    : 'bg-slate-800 text-emerald-300 border-emerald-500/30 hover:bg-slate-700'
                }`}
                title="انتخاب صدای گوینده"
              >
                <option value="fa-IR-DilaraNeural">خانم دلارا</option>
                <option value="fa-IR-FaridNeural">آقای فرید</option>
              </select>

              {/* کلید بستن */}
              <button
                onClick={() => {
                  stopAudio()
                  stopListening()
                  setIsOpen(false)
                }}
                className={`p-1.5 rounded-lg transition-colors ${
                  isLight ? 'text-slate-400 hover:text-slate-900 hover:bg-slate-100' : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* نوار وضعیت صوتی و کنترل‌ها */}
          <div className={`px-4 py-2 border-b flex items-center justify-between text-xs ${
            isLight ? 'bg-emerald-50/40 border-emerald-100' : 'bg-slate-800/60 border-slate-700/50'
          }`}>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setAutoSpeakEnabled(!autoSpeakEnabled)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg transition-colors font-medium ${
                  autoSpeakEnabled
                    ? isLight
                      ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : isLight
                    ? 'bg-slate-100 text-slate-500'
                    : 'bg-slate-700/50 text-slate-400'
                }`}
                title="خواندن خودکار پاسخ‌ها با صوت فارسی"
              >
                {autoSpeakEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
                <span>پخش خودکار صوت: {autoSpeakEnabled ? 'روشن' : 'خاموش'}</span>
              </button>

              {isSpeaking && (
                <button
                  onClick={stopAudio}
                  className="flex items-center gap-1 px-2 py-1 rounded bg-rose-500/20 text-rose-600 hover:bg-rose-500/30 border border-rose-500/30 transition-colors font-bold"
                  title="توقف پخش صوت"
                >
                  <Square className="w-3 h-3 fill-current" />
                  <span>توقف صوت</span>
                </button>
              )}
            </div>

            {/* وضعیت انیمیشن صدا */}
            {isSpeaking && (
              <div className="flex items-center gap-1 text-emerald-600 font-medium">
                <span className="w-1.5 h-3 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1.5 h-4 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1.5 h-2 bg-emerald-500 rounded-full animate-bounce" />
                <span className="mr-1">در حال صحبت...</span>
              </div>
            )}
          </div>

          {/* هشدار راهنمای صوتی هنگام خطا در آزمایشگاه */}
          {lastErrorCode && (
            <div className={`px-4 py-2.5 border-b flex items-center justify-between text-xs ${
              isLight
                ? 'bg-amber-50 border-amber-200 text-amber-950'
                : 'bg-gradient-to-r from-amber-950/60 to-slate-900 border-amber-500/30 text-amber-200'
            }`}>
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-500 shrink-0" />
                <span className="font-medium">خطای آزمایشگاهی شناسایی شد.</span>
              </div>
              <button
                onClick={handleVoiceErrorExplanation}
                disabled={isProcessing}
                className="flex items-center gap-1 px-2.5 py-1 bg-amber-400 text-slate-950 font-black rounded-lg hover:bg-amber-300 transition-colors shadow-sm disabled:opacity-50"
              >
                <Volume2 className="w-3.5 h-3.5" />
                <span>توضیح صوتی علت</span>
              </button>
            </div>
          )}

          {/* محتوای پیام‌ها و تاریخچه گفتگو */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${
                  msg.sender === 'user' ? 'items-start' : 'items-end'
                }`}
              >
                <div
                  className={`max-w-[88%] p-3.5 rounded-2xl shadow-sm ${
                    msg.sender === 'user'
                      ? 'bg-emerald-600 text-white rounded-br-none'
                      : isLight
                      ? 'bg-slate-50 text-slate-800 border border-slate-200 rounded-bl-none'
                      : 'bg-slate-800/90 text-slate-100 border border-slate-700/80 rounded-bl-none'
                  }`}
                >
                  <p className="leading-relaxed whitespace-pre-line text-sm">{msg.text}</p>
                  
                  {/* دکمه خواندن مجدد پاسخ توسط گوینده */}
                  {msg.sender === 'ai' && (
                    <div className={`mt-2.5 pt-2 border-t flex items-center justify-between text-[11px] ${
                      isLight ? 'border-slate-200 text-slate-500' : 'border-slate-700/50 text-slate-400'
                    }`}>
                      <span>{msg.timestamp}</span>
                      <button
                        onClick={() => speakText(msg.text)}
                        className={`flex items-center gap-1 transition-colors font-bold px-1.5 py-0.5 rounded ${
                          isLight ? 'text-emerald-700 hover:text-emerald-900 hover:bg-emerald-50' : 'text-emerald-400 hover:text-emerald-300 hover:bg-slate-700/50'
                        }`}
                        title="پخش با صدای گوینده"
                      >
                        <Volume2 className="w-3.5 h-3.5" />
                        <span>پخش صوتی</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* نشانگر رونویسی زنده گفتار دانش‌آموز */}
            {isListening && (
              <div className="flex flex-col items-start animate-pulse">
                <div className={`p-3 rounded-2xl border ${
                  isLight
                    ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
                    : 'bg-emerald-950/80 border-emerald-500/40 text-emerald-200'
                }`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                    <span className="font-bold text-[11px]">در حال شنیدن صدای شما...</span>
                  </div>
                  <p className="text-sm font-medium italic">
                    {liveTranscript || 'لطفاً صحبت کنید...'}
                  </p>
                </div>
              </div>
            )}

            {/* نشانگر در حال پردازش */}
            {isProcessing && (
              <div className={`flex items-center gap-2 p-2.5 rounded-xl border w-fit ${
                isLight ? 'bg-slate-100 text-slate-600 border-slate-200' : 'bg-slate-800/60 text-slate-400 border-slate-700/50'
              }`}>
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" />
                <span className="font-medium">معلم‌یار در حال تحلیل علمی است...</span>
              </div>
            )}

            {/* خطای دسترسی میکروفون */}
            {hasVoiceError && (
              <div className={`p-3 rounded-xl border text-xs ${
                isLight ? 'bg-rose-50 border-rose-200 text-rose-800' : 'bg-rose-950/80 border-rose-500/40 text-rose-200'
              }`}>
                {voiceErrorMessage}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* پرسش‌های صوتی پیشنهادی و سریع */}
          <div className={`px-4 py-2.5 border-t ${
            isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-800/40 border-slate-700/40'
          }`}>
            <p className={`text-[11px] mb-1.5 flex items-center gap-1 font-bold ${
              isLight ? 'text-slate-600' : 'text-slate-400'
            }`}>
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>پیشنهادهای صوتی سریع (کلیک یا بیان صوتی):</span>
            </p>
            <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
              {voicePrompts.slice(0, 3).map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendVoiceQuestion(prompt)}
                  disabled={isProcessing}
                  className={`shrink-0 text-[11px] px-2.5 py-1 rounded-full transition-colors truncate max-w-[200px] font-semibold border ${
                    isLight
                      ? 'bg-white hover:bg-emerald-50 text-emerald-800 border-emerald-200 shadow-xs'
                      : 'bg-slate-800 hover:bg-slate-700 text-emerald-300 border-emerald-500/20'
                  }`}
                  title={prompt}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* نوار ورودی گفتار و متن */}
          <div className={`p-3 border-t flex flex-col gap-2 ${
            isLight ? 'bg-white border-slate-200' : 'bg-slate-950 border-emerald-500/20'
          }`}>
            
            {/* دکمه مرکزی ضبط صوت بزرگ و تعاملی */}
            <div className="flex items-center justify-center">
              <button
                onClick={isListening ? stopListening : startListening}
                disabled={isProcessing}
                className={`relative flex items-center justify-center w-14 h-14 rounded-full shadow-lg transition-all duration-300 ${
                  isListening
                    ? 'bg-rose-600 text-white shadow-rose-500/50 scale-110 animate-pulse'
                    : 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-emerald-500/30 hover:scale-105'
                }`}
                title={isListening ? 'پایان ضبط و ارسال' : 'شروع صحبت صوتی'}
              >
                {isListening ? (
                  <>
                    <MicOff className="w-7 h-7" />
                    <span className="absolute inset-0 rounded-full border-2 border-rose-400 animate-ping pointer-events-none" />
                  </>
                ) : (
                  <Mic className="w-7 h-7" />
                )}
              </button>
            </div>
            
            <p className={`text-center text-[11px] ${isLight ? 'text-slate-500 font-medium' : 'text-slate-400'}`}>
              {isListening ? 'در حال شنیدن... برای پایان و ارسال دوباره کلیک کنید' : 'برای صحبت صوتی روی میکروفون کلیک کنید'}
            </p>

            {/* ورودی متنی آلترناتیو */}
            <div className="flex items-center gap-2 pt-1">
              <input
                type="text"
                value={questionInput}
                onChange={(e) => setQuestionInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendVoiceQuestion(questionInput)}
                placeholder="یا سوال خود را اینجا تایپ کنید..."
                disabled={isProcessing || isListening}
                className={`flex-1 text-xs rounded-xl px-3 py-2 border transition-colors outline-none ${
                  isLight
                    ? 'bg-slate-50 text-slate-900 placeholder-slate-400 border-slate-200 focus:border-emerald-500'
                    : 'bg-slate-800/90 text-white placeholder-slate-400 border-slate-700 focus:border-emerald-500'
                }`}
              />
              <button
                onClick={() => handleSendVoiceQuestion(questionInput)}
                disabled={!questionInput.trim() || isProcessing}
                className="p-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded-xl transition-colors"
                title="ارسال متنی"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>

        </div>
      )}
    </aside>
  )
}
