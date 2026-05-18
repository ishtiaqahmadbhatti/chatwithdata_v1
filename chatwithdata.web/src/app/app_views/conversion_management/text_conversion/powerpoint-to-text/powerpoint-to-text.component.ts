import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseTextToolComponent } from '../base-text-tool.component';

@Component({
  selector: 'app-powerpoint-to-text',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './powerpoint-to-text.component.html',
  styleUrl: './powerpoint-to-text.component.css',
  standalone: true
})
export class PowerpointToTextComponent extends BaseTextToolComponent {
  toolId = 'powerpoint-to-text';
}
