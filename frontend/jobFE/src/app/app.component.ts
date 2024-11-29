import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { JobComponent } from './job.component';
import { NavComponent } from './nav.component'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, JobComponent, NavComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'jobFE';
}
