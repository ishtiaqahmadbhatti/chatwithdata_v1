import { Component, ViewChild, ElementRef, OnDestroy, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpEventType } from '@angular/common/http';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseAudioToolComponent } from '../base-audio-tool.component';

interface AudioSegment {
  start: string;
  end: string;
}

@Component({
  selector: 'app-trim-audio',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './trim-audio.component.html',
  styleUrl: './trim-audio.component.css',
  standalone: true
})
export class TrimAudioComponent extends BaseAudioToolComponent implements OnDestroy {
  toolId = 'trim-audio';
  segments: AudioSegment[] = [{ start: '00:00', end: '00:10' }];

  audioUrl: SafeUrl | null = null;
  objectUrl: string | null = null;

  private sanitizer = inject(DomSanitizer);
  private cdr = inject(ChangeDetectorRef);

  @ViewChild('audioPlayer') audioPlayer!: ElementRef<HTMLAudioElement>;

  override onFileSelected(file: File) {
    super.onFileSelected(file);

    // Setup preview
    if (this.objectUrl) {
      URL.revokeObjectURL(this.objectUrl);
    }
    this.objectUrl = URL.createObjectURL(file);
    this.audioUrl = this.sanitizer.bypassSecurityTrustUrl(this.objectUrl);

    // Force rendering and reload audio player to ensure it picks up the new source
    this.cdr.detectChanges();
    setTimeout(() => {
      if (this.audioPlayer && this.audioPlayer.nativeElement && this.objectUrl) {
        this.audioPlayer.nativeElement.src = this.objectUrl;
        this.audioPlayer.nativeElement.load();
      }
    }, 100);
  }

  override reset() {
    // Revoke output URL if it exists
    if (this.conversionResult && this.conversionResult.downloadUrl.startsWith('blob:')) {
      URL.revokeObjectURL(this.conversionResult.downloadUrl);
    }

    super.reset();

    // Revoke preview URL
    if (this.objectUrl) {
      URL.revokeObjectURL(this.objectUrl);
    }
    this.objectUrl = null;
    this.audioUrl = null;
    this.segments = [{ start: '00:00', end: '00:10' }];
  }

  onAudioError(event: any) {
    console.error("Audio playback error", event);
    alert("Error loading audio file. The format might not be supported by your browser.");
  }

  ngOnDestroy() {
    if (this.objectUrl) {
      URL.revokeObjectURL(this.objectUrl);
    }
  }

  override convert() {
    if (!this.selectedFile) {
      this.toastService.show('Please select a file first', 'error');
      return;
    }

    const validSegments = this.segments.filter(s => s.start.trim() !== '' && s.end.trim() !== '');
    if (validSegments.length === 0) {
      this.toastService.show('Please provide at least one valid timing segment', 'error');
      return;
    }

    const segmentsJson = JSON.stringify(validSegments);

    this.isConverting = true;
    this.conversionResult = null;
    this.uploadProgress = 0;
    this.conversionStatus = 'Initializing...';

    // Use standard ConvertFile which returns JSON with a download_url
    this.audioService.ConvertFile(this.toolId, this.selectedFile, this.outputFilename, { segments: segmentsJson })
      .subscribe({
        next: (event: any) => {
          switch (event.type) {
            case HttpEventType.Sent:
              this.conversionStatus = 'Request sent...';
              break;
            case HttpEventType.UploadProgress:
              if (event.total) {
                this.uploadProgress = Math.round(100 * event.loaded / event.total);
              } else {
                this.uploadProgress = 50;
              }
              this.conversionStatus = `File Uploading... ${this.uploadProgress}%`;
              break;
            case HttpEventType.Response:
              this.uploadProgress = 100;
              this.conversionStatus = 'Finalizing...';

              const response = event.body;
              if (response && response.success && response.download_url) {
                this.conversionResult = {
                  downloadUrl: response.download_url,
                  fileName: response.output_filename || 'trimmed_audio'
                };

                this.isConverting = false;
                this.toastService.show('File converted successfully. Ready to save.', 'success');
              } else {
                this.handleError(response?.message || 'Conversion failed');
              }
              break;
          }
        },
        error: (err) => {
          this.handleError(err);
        }
      });
  }

  captureTime(index: number, type: 'start' | 'end') {
    if (!this.audioPlayer || !this.audioPlayer.nativeElement) return;
    const time = this.audioPlayer.nativeElement.currentTime;
    const formatted = this.formatTime(time);
    if (type === 'start') {
      this.segments[index].start = formatted;
    } else {
      this.segments[index].end = formatted;
    }
  }

  formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    const pad = (n: number) => n < 10 ? '0' + n : n;
    return `${pad(mins)}:${pad(secs)}.${pad(ms)}`;
  }

  addSegment() {
    this.segments.push({ start: '', end: '' });
  }

  removeSegment(index: number) {
    if (this.segments.length > 1) {
      this.segments.splice(index, 1);
    }
  }


}
