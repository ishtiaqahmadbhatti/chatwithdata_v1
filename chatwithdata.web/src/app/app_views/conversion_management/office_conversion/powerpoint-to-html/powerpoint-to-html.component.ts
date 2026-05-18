import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseOfficeToolComponent } from '../base-office-tool.component';

@Component({
  selector: 'app-powerpoint-to-html',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './powerpoint-to-html.component.html',
  styleUrl: './powerpoint-to-html.component.css',
  standalone: true
})
export class PowerpointToHtmlComponent extends BaseOfficeToolComponent {
  toolId = 'powerpoint-to-html';
}
