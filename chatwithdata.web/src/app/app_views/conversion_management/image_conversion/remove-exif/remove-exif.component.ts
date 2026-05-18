import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseImageToolComponent } from '../base-image-tool.component';

@Component({
  selector: 'app-remove-exif',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './remove-exif.component.html',
  styleUrl: './remove-exif.component.css',
  standalone: true
})
export class RemoveExifComponent extends BaseImageToolComponent {
  toolId = 'remove-exif';
}
