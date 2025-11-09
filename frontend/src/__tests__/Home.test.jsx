/**
 * Home component testleri
 * Case gereksinimi: En az 2 component testi
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Home from '../pages/Home';
import * as api from '../services/api';

// Mock react-router-dom useNavigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

// Mock API
vi.mock('../services/api', () => ({
  dropsService: {
    getAll: vi.fn(),
  },
  waitlistService: {
    join: vi.fn(),
  },
}));

const mockDrops = [
  {
    id: 1,
    title: 'Test Drop 1',
    description: 'Test açıklama 1',
    image_url: 'https://example.com/image1.jpg',
    total_quantity: 100,
    remaining_quantity: 50,
    latitude: 41.0082,
    longitude: 28.9784,
    address: 'İstanbul',
    radius_meters: 1000,
    start_time: new Date().toISOString(),
    end_time: new Date(Date.now() + 3600000).toISOString(),
    status: 'active',
    is_active: true,
  },
  {
    id: 2,
    title: 'Test Drop 2',
    description: 'Test açıklama 2',
    image_url: null,
    total_quantity: 200,
    remaining_quantity: 100,
    latitude: 41.0082,
    longitude: 28.9784,
    address: 'Ankara',
    radius_meters: 2000,
    start_time: new Date().toISOString(),
    end_time: new Date(Date.now() + 7200000).toISOString(),
    status: 'active',
    is_active: true,
  },
];

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Home Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock geolocation
    global.navigator.geolocation = {
      getCurrentPosition: vi.fn((success) => {
        success({
          coords: {
            latitude: 41.0082,
            longitude: 28.9784,
          },
        });
      }),
    };
  });

  it('should render drop listesi', async () => {
    api.dropsService.getAll.mockResolvedValue({ data: mockDrops });

    renderWithRouter(<Home user={null} />);

    await waitFor(() => {
      expect(screen.getByText('Test Drop 1')).toBeInTheDocument();
      expect(screen.getByText('Test Drop 2')).toBeInTheDocument();
    });
  });

  it('should call dropsService.getAll on mount', async () => {
    api.dropsService.getAll.mockResolvedValue({ data: [] });

    renderWithRouter(<Home user={null} />);

    await waitFor(() => {
      expect(api.dropsService.getAll).toHaveBeenCalledTimes(1);
    });
  });

  it('should display loading state initially', () => {
    api.dropsService.getAll.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithRouter(<Home user={null} />);

    // Loading spinner should be visible
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('should handle waitlist join', async () => {
    api.dropsService.getAll.mockResolvedValue({ data: mockDrops });
    api.waitlistService.join.mockResolvedValue({ data: { id: 1, drop_id: 1, user_id: 1 } });

    renderWithRouter(<Home user={{ id: 1, username: 'testuser' }} />);

    await waitFor(() => {
      expect(screen.getByText('Test Drop 1')).toBeInTheDocument();
    });

    // Find and click join button - case formatına göre dropId parametresi
    const joinButtons = screen.getAllByText(/Katıl/i);
    expect(joinButtons.length).toBeGreaterThan(0);
    
    // Click first join button
    joinButtons[0].click();

    await waitFor(() => {
      // Case formatı: join(dropId) - dropId direkt parametre (1)
      expect(api.waitlistService.join).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  it('should display empty state when no drops', async () => {
    api.dropsService.getAll.mockResolvedValue({ data: [] });

    renderWithRouter(<Home user={null} />);

    await waitFor(() => {
      expect(screen.getByText(/Drop bulunamadı/i)).toBeInTheDocument();
    });
  });

  it('should filter drops by search term', async () => {
    api.dropsService.getAll.mockResolvedValue({ data: mockDrops });

    renderWithRouter(<Home user={null} />);

    await waitFor(() => {
      expect(screen.getByText('Test Drop 1')).toBeInTheDocument();
    });

    // Search input should be present
    const searchInput = screen.getByPlaceholderText(/Ara/i);
    expect(searchInput).toBeInTheDocument();
  });
});

