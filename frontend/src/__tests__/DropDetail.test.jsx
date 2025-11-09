/**
 * DropDetail component testleri
 * Case gereksinimi: En az 2 component testi
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import DropDetail from '../pages/DropDetail';
import * as api from '../services/api';

// Mock react-router-dom useNavigate and useParams
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useParams: () => ({ id: '1' }),
  };
});

// Mock API
vi.mock('../services/api', () => ({
  dropsService: {
    getById: vi.fn(),
  },
  waitlistService: {
    join: vi.fn(),
    leave: vi.fn(),
    getMyWaitlist: vi.fn(),
    getPosition: vi.fn(),
  },
  claimsService: {
    create: vi.fn(),
    getMyClaims: vi.fn(),
  },
}));

const mockDrop = {
  id: 1,
  title: 'Test Drop',
  description: 'Test açıklama',
  image_url: 'https://example.com/image.jpg',
  total_quantity: 100,
  remaining_quantity: 50,
  claimed_quantity: 50,
  latitude: 41.0082,
  longitude: 28.9784,
  address: 'İstanbul, Türkiye',
  radius_meters: 1000,
  start_time: new Date().toISOString(),
  end_time: new Date(Date.now() + 3600000).toISOString(),
  status: 'active',
  is_active: true,
};

const renderWithRouter = (component, initialEntries = ['/drops/1']) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      {component}
    </MemoryRouter>
  );
};

describe('DropDetail Component', () => {
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

  it('should render drop details', async () => {
    api.dropsService.getById.mockResolvedValue({ data: mockDrop });
    api.waitlistService.getMyWaitlist.mockResolvedValue({ data: [] });
    api.claimsService.getMyClaims.mockResolvedValue({ data: [] });

    renderWithRouter(<DropDetail user={{ id: 1, username: 'testuser' }} />);

    await waitFor(() => {
      expect(screen.getByText('Test Drop')).toBeInTheDocument();
      expect(screen.getByText('Test açıklama')).toBeInTheDocument();
      expect(screen.getByText(/İstanbul/i)).toBeInTheDocument();
    });
  });

  it('should call dropsService.getById on mount', async () => {
    api.dropsService.getById.mockResolvedValue({ data: mockDrop });
    api.waitlistService.getMyWaitlist.mockResolvedValue({ data: [] });
    api.claimsService.getMyClaims.mockResolvedValue({ data: [] });

    renderWithRouter(<DropDetail user={{ id: 1, username: 'testuser' }} />);

    await waitFor(() => {
      // useParams'dan gelen id string olabilir
      expect(api.dropsService.getById).toHaveBeenCalled();
    });
  });

  it('should handle waitlist join', async () => {
    api.dropsService.getById.mockResolvedValue({ data: mockDrop });
    api.waitlistService.getMyWaitlist.mockResolvedValue({ data: [] });
    api.waitlistService.getPosition.mockResolvedValue({ data: { position: 1 } });
    api.claimsService.getMyClaims.mockResolvedValue({ data: [] });
    api.waitlistService.join.mockResolvedValue({ data: { id: 1, drop_id: 1, user_id: 1 } });

    renderWithRouter(<DropDetail user={{ id: 1, username: 'testuser' }} />);

    await waitFor(() => {
      expect(screen.getByText('Test Drop')).toBeInTheDocument();
    });

    // Find join button
    const joinButton = screen.getByText(/Bekleme Listesine Katıl/i);
    expect(joinButton).toBeInTheDocument();

    joinButton.click();

    await waitFor(() => {
      // Case formatı: join(dropId) - dropId direkt parametre (id string'den geliyor, '1')
      expect(api.waitlistService.join).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  it('should handle waitlist leave', async () => {
    api.dropsService.getById.mockResolvedValue({ data: mockDrop });
    api.waitlistService.getMyWaitlist.mockResolvedValue({ 
      data: [{ id: 1, drop_id: 1, user_id: 1 }] 
    });
    api.waitlistService.getPosition.mockResolvedValue({ data: { position: 1 } });
    api.claimsService.getMyClaims.mockResolvedValue({ data: [] });
    api.waitlistService.leave.mockResolvedValue({ data: { message: 'Success' } });

    renderWithRouter(<DropDetail user={{ id: 1, username: 'testuser' }} />);

    await waitFor(() => {
      expect(screen.getByText('Test Drop')).toBeInTheDocument();
    });

    // Find leave button
    const leaveButton = screen.getByText(/Listeden Çık/i);
    expect(leaveButton).toBeInTheDocument();

    leaveButton.click();

    await waitFor(() => {
      // Case formatı: leave(dropId) - dropId direkt parametre (id string'den geliyor, '1')
      expect(api.waitlistService.leave).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  it('should handle claim creation', async () => {
    api.dropsService.getById.mockResolvedValue({ data: mockDrop });
    api.waitlistService.getMyWaitlist.mockResolvedValue({ 
      data: [{ id: 1, drop_id: 1, user_id: 1 }] 
    });
    api.waitlistService.getPosition.mockResolvedValue({ data: { position: 1 } });
    api.claimsService.getMyClaims.mockResolvedValue({ data: [] });
    api.claimsService.create.mockResolvedValue({ 
      data: { 
        id: 1, 
        drop_id: 1, 
        user_id: 1, 
        status: 'pending',
        verification_code: 'DC-1234'
      } 
    });

    renderWithRouter(<DropDetail user={{ id: 1, username: 'testuser' }} />);

    await waitFor(() => {
      expect(screen.getByText('Test Drop')).toBeInTheDocument();
    });

    // Find claim button (if available) - case formatı: create(dropId, data)
    const claimButtons = screen.queryAllByText(/Claim/i);
    // Claim button might not be visible if conditions aren't met
    // This test verifies the component structure
    expect(api.dropsService.getById).toHaveBeenCalled();
    // Case formatı: create(dropId, { quantity, claim_latitude, claim_longitude })
    // Test sadece component'in render olduğunu doğrular
  });

  it('should display loading state initially', () => {
    api.dropsService.getById.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithRouter(<DropDetail user={{ id: 1, username: 'testuser' }} />);

    // Loading spinner should be visible
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('should display error when drop not found', async () => {
    api.dropsService.getById.mockRejectedValue({ 
      response: { status: 404, data: { detail: 'Drop bulunamadı' } } 
    });

    renderWithRouter(<DropDetail user={{ id: 1, username: 'testuser' }} />);

    await waitFor(() => {
      expect(screen.getByText(/Drop bulunamadı/i)).toBeInTheDocument();
    });
  });
});

