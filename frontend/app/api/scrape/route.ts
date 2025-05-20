import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(req: Request) {
  try {
    const { startDate, endDate, maxProductsPerDay, maxTotalProducts } = await req.json();

    // Validate input
    if (!startDate || !endDate) {
      return NextResponse.json(
        { error: 'Start date and end date are required' },
        { status: 400 }
      );
    }

    // Start the scraping process
    const scraperPath = path.join(process.cwd(), '..', 'backend', 'scraper.py');
    const pythonProcess = spawn('python3', [
      scraperPath,
      '--start-date', startDate,
      '--end-date', endDate,
      '--max-products-per-day', maxProductsPerDay.toString(),
      '--max-total-products', maxTotalProducts.toString()
    ]);

    // Handle process output
    pythonProcess.stdout.on('data', (data) => {
      console.log(`Scraper output: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Scraper error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      console.log(`Scraper process exited with code ${code}`);
    });

    return NextResponse.json({ success: true, message: 'Scraping process started' });
  } catch (error) {
    console.error('Error starting scraping process:', error);
    return NextResponse.json(
      { error: 'Failed to start scraping process' },
      { status: 500 }
    );
  }
} 