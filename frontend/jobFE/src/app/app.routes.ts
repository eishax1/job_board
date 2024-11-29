import { Routes } from '@angular/router';
import { HomeComponent } from './home.component';
import { JobComponent } from './job.component';
import { singleJobComponent } from './singleJob.component';

export const routes: Routes = [
    {
    path: '',
    component: HomeComponent
    },
    {
    path: 'job',
    component: JobComponent
    },
    {
        path: 'job/:id',
        component: singleJobComponent
        }
    ];
