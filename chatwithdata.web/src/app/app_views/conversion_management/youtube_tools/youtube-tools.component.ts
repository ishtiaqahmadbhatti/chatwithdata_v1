import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { YoutubeToolsService } from '../../../app_services/youtube_tools.service';
import { ToastService } from '../../../app_services/toast';

@Component({
  selector: 'app-youtube-tools',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './youtube-tools.component.html',
  styleUrls: ['./youtube-tools.component.css']
})
export class YoutubeToolsComponent {
  private youtubeService = inject(YoutubeToolsService);
  private toastService = inject(ToastService);
  private sanitizer = inject(DomSanitizer);

  videoUrl: string = '';
  quality: string = 'highest';

  // Loading states
  isExtracting: boolean = false;
  isDownloading: boolean = false;
  downloadProgress: number = 0;

  // Extracted Data
  videoData: any = null;
  activeTab: string = 'details';

  extractData(): void {
    if (!this.videoUrl) {
      this.toastService.show('Please enter a YouTube video URL', 'error');
      return;
    }

    this.isExtracting = true;
    this.videoData = null;

    this.youtubeService.extractData(this.videoUrl).subscribe({
      next: (res) => {
        debugger;
        this.videoData = res.data;
        this.isExtracting = false;
        this.toastService.show('YouTube data extracted successfully!', 'success');
      },
      error: (err) => {
        console.error('Extraction error:', err);
        this.isExtracting = false;
        this.toastService.show(err?.error?.detail || 'Failed to extract YouTube data', 'error');
      }
    });
  }

  downloadVideo(): void {
    if (!this.videoUrl) {
      this.toastService.show('Please enter a YouTube video URL', 'error');
      return;
    }

    this.isDownloading = true;
    this.downloadProgress = 20;

    this.youtubeService.downloadVideo(this.videoUrl, this.quality).subscribe({
      next: (res) => {
        this.downloadProgress = 60;
        if (res && res.filename) {
          this.downloadProgress = 80;
          this.youtubeService.downloadFile(res.filename).subscribe({
            next: (blob) => {
              this.downloadProgress = 100;
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = res.filename;
              document.body.appendChild(a);
              a.click();
              window.URL.revokeObjectURL(url);
              document.body.removeChild(a);

              setTimeout(() => {
                this.isDownloading = false;
                this.downloadProgress = 0;
              }, 1000);

              this.toastService.show('Video downloaded successfully!', 'success');
            },
            error: (err) => {
              console.error('File serving error:', err);
              this.isDownloading = false;
              this.downloadProgress = 0;
              this.toastService.show('Failed to download the video file', 'error');
            }
          });
        } else {
          this.isDownloading = false;
          this.downloadProgress = 0;
          this.toastService.show('Download failed: No filename returned', 'error');
        }
      },
      error: (err) => {
        console.error('Download error:', err);
        this.isDownloading = false;
        this.downloadProgress = 0;
        this.toastService.show(err?.error?.detail || 'Failed to start video download', 'error');
      }
    });
  }

  getEmbedUrl(): SafeResourceUrl | null {
    if (!this.videoUrl) return null;
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = this.videoUrl.match(regExp);
    if (match && match[2].length === 11) {
      const secureUrl = `https://www.youtube.com/embed/${match[2]}`;
      return this.sanitizer.bypassSecurityTrustResourceUrl(secureUrl);
    }
    return null;
  }
}
