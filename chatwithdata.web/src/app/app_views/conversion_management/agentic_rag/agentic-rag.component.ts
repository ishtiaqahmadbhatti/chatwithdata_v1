import { Component, OnInit, inject, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RagToolsService } from '../../../app_services/rag_tools.service';
import { YoutubeToolsService } from '../../../app_services/youtube_tools.service';
import { ToastService } from '../../../app_services/toast';

interface Message {
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

@Component({
  selector: 'app-agentic-rag',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './agentic-rag.component.html',
  styleUrls: ['./agentic-rag.component.css']
})
export class AgenticRagComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatScrollContainer') private chatScrollContainer!: ElementRef;

  private ragService = inject(RagToolsService);
  private youtubeService = inject(YoutubeToolsService);
  private toastService = inject(ToastService);

  // Ingestion State
  videoUrl: string = '';
  isIngesting: boolean = false;

  // Active Session & Chat State
  activeSession: any = null;
  queryText: string = '';
  isQuerying: boolean = false;
  chatHistory: Message[] = [];

  // Session List
  sessions: any[] = [];
  isLoadingSessions: boolean = false;

  ngOnInit(): void {
    this.loadSessions();
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  loadSessions(): void {
    this.isLoadingSessions = true;
    this.ragService.getSessions().subscribe({
      next: (res) => {
        this.sessions = Array.isArray(res) ? res : (res.sessions || []);
        this.isLoadingSessions = false;
      },
      error: (err) => {
        console.error('Error loading sessions:', err);
        this.isLoadingSessions = false;
      }
    });
  }

  ingestVideo(): void {
    if (!this.videoUrl) {
      this.toastService.show('Please enter a YouTube video URL to ingest', 'error');
      return;
    }

    this.isIngesting = true;
    
    // Step 1: Extract Video Metadata, Transcript, and Comments
    this.youtubeService.extractData(this.videoUrl).subscribe({
      next: (extractedData) => {
        this.toastService.show('Video extracted! Building AI index...', 'success');
        
        // Step 2: Push Extracted Data into FAISS/Agentic RAG
        this.ragService.ingestVideo({ data: extractedData }).subscribe({
          next: (res) => {
            this.isIngesting = false;
            this.videoUrl = '';
            this.toastService.show('Video ingested and indexed successfully!', 'success');
            this.loadSessions();
            
            // Auto-select the newly ingested video
            if (res && res.video_id) {
              this.selectSession({
                video_id: res.video_id,
                title: res.title || extractedData.title || 'Ingested Video',
                thumbnail: res.thumbnail || extractedData.thumbnail
              });
            } else if (res && res.session) {
              this.selectSession(res.session);
            }
          },
          error: (err) => {
            console.error('Ingestion error:', err);
            this.isIngesting = false;
            this.toastService.show(err?.error?.detail || 'Failed to ingest video into AI', 'error');
          }
        });
      },
      error: (err) => {
        console.error('Extraction error:', err);
        this.isIngesting = false;
        this.toastService.show(err?.error?.detail || 'Failed to extract YouTube metadata', 'error');
      }
    });
  }

  selectSession(session: any): void {
    this.activeSession = session;
    this.chatHistory = [
      {
        sender: 'ai',
        text: `Hello! I have fully parsed and understood the video: "${session.title}". You can ask me any question about its details, arguments, transcripts, or specifics. How can I help you today?`,
        timestamp: new Date()
      }
    ];
    this.queryText = '';
  }

  sendQuery(): void {
    if (!this.queryText.trim() || !this.activeSession) return;

    const userMsg = this.queryText.trim();
    this.chatHistory.push({
      sender: 'user',
      text: userMsg,
      timestamp: new Date()
    });

    this.queryText = '';
    this.isQuerying = true;

    this.ragService.queryVideo(this.activeSession.video_id, userMsg).subscribe({
      next: (res) => {
        this.chatHistory.push({
          sender: 'ai',
          text: res.answer || res.response || 'I was unable to find an answer in the video content.',
          timestamp: new Date()
        });
        this.isQuerying = false;
      },
      error: (err) => {
        console.error('Query error:', err);
        this.chatHistory.push({
          sender: 'ai',
          text: 'Sorry, I encountered an error while processing your request. Please try again.',
          timestamp: new Date()
        });
        this.isQuerying = false;
      }
    });
  }

  removeSession(session: any, event: Event): void {
    event.stopPropagation();
    
    if (confirm(`Are you sure you want to remove the session for "${session.title}"?`)) {
      this.ragService.removeSession(session.video_id).subscribe({
        next: () => {
          this.toastService.show('Session removed successfully', 'success');
          if (this.activeSession && this.activeSession.video_id === session.video_id) {
            this.activeSession = null;
            this.chatHistory = [];
          }
          this.loadSessions();
        },
        error: (err) => {
          console.error('Error removing session:', err);
          this.toastService.show('Failed to remove session', 'error');
        }
      });
    }
  }

  private scrollToBottom(): void {
    try {
      this.chatScrollContainer.nativeElement.scrollTop = this.chatScrollContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }
}
