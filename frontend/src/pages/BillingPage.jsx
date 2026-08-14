import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { billingApi } from '../api/client';
import {
  FileText, Download, CheckCircle2, AlertCircle, RefreshCw, CreditCard,
  Building, Calendar, User, ArrowLeft, Sparkles, ShieldCheck, Clock
} from 'lucide-react';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const BillingPage = () => {
  const { invoiceId, bookingId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [paying, setPaying] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [paymentNotice, setPaymentNotice] = useState(null);

  const fetchInvoiceData = async () => {
    setLoading(true);
    setError('');
    setPaymentNotice(null);
    try {
      let targetId = invoiceId || searchParams.get('id');
      let res;
      
      if (targetId) {
        res = await billingApi.getInvoice(targetId);
      } else if (bookingId) {
        res = await billingApi.getInvoiceByBooking(bookingId);
      } else {
        // Fallback to default demo booking invoice
        res = await billingApi.getInvoiceByBooking('demo-booking-001').catch(() =>
          billingApi.getInvoice('TMAI-INV-2026-000001')
        );
      }

      if (res.data?.invoice) {
        setInvoice(res.data.invoice);
      } else {
        setError('Unable to load billing information.');
      }
    } catch (err) {
      console.error("Billing fetch error:", err);
      setError(err.userFriendlyMessage || 'Unable to load billing information.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoiceData();
  }, [invoiceId, bookingId]);

  const handleDemoPayment = async (simulateFailure = false) => {
    if (!invoice?.id && !invoice?.invoice_number) return;
    setPaying(true);
    setPaymentNotice(null);
    try {
      const invIdentifier = invoice.id || invoice.invoice_number;
      const res = await billingApi.processDemoPayment(invIdentifier, simulateFailure);
      if (res.data?.invoice) {
        setInvoice(res.data.invoice);
      }
      if (res.data?.success) {
        setPaymentNotice({
          type: 'success',
          message: res.data.message || 'Demo payment successful. No real money was charged.'
        });
      } else {
        setPaymentNotice({
          type: 'error',
          message: res.data?.message || 'Demo payment failed. Please try again.'
        });
      }
    } catch (err) {
      setPaymentNotice({
        type: 'error',
        message: err.userFriendlyMessage || 'Demo payment failed. Please try again.'
      });
    } finally {
      setPaying(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!invoice?.id && !invoice?.invoice_number) return;
    setDownloading(true);
    try {
      const invIdentifier = invoice.id || invoice.invoice_number;
      const res = await billingApi.downloadInvoicePdf(invIdentifier);
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice-${invoice.invoice_number || 'TMAI-INV'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("PDF download failed:", err);
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 space-y-6">
        <LoadingSkeleton count={3} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center space-y-6">
        <div className="glass-panel rounded-3xl p-8 border border-gray-800 space-y-4">
          <AlertCircle className="w-12 h-12 text-rose-400 mx-auto" />
          <h2 className="text-xl font-bold text-white">Billing Information Unavailable</h2>
          <p className="text-xs text-gray-400">{error}</p>
          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={fetchInvoiceData}
              className="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-white font-bold text-xs flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" /> Retry
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-5 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-semibold text-xs"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  const isPaid = invoice?.payment_status === 'Paid';
  const isFailed = invoice?.payment_status === 'Failed';

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Top Header Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="text-xs text-gray-400 hover:text-white font-semibold flex items-center gap-1.5 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadPdf}
            disabled={downloading}
            className="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-bold text-xs flex items-center gap-2 border border-gray-700 transition-all"
          >
            <Download className="w-4 h-4 text-cyan-400" />
            {downloading ? 'Generating PDF...' : 'Download Invoice'}
          </button>
        </div>
      </div>

      {/* Demo Banner Notification */}
      <div className="p-3.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-cyan-400 flex-shrink-0" />
          <span className="font-semibold">Demo Payment — No real money was charged.</span>
        </div>
        <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">
          Sandbox Mode
        </span>
      </div>

      {/* Payment Action Notice Banner */}
      {paymentNotice && (
        <div className={`p-4 rounded-2xl border text-xs flex items-center gap-3 ${
          paymentNotice.type === 'success'
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
        }`}>
          {paymentNotice.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
          )}
          <span className="font-bold">{paymentNotice.message}</span>
        </div>
      )}

      {/* Main Printable Invoice Card */}
      <div className="glass-panel rounded-3xl p-8 border border-gray-800 space-y-8 shadow-2xl relative overflow-hidden">
        {/* Subtle Background Glow */}
        <div className="absolute right-0 top-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl -z-10" />

        {/* Invoice Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-6 border-b border-gray-800">
          <div>
            <div className="flex items-center gap-2 text-cyan-400 font-black text-xl tracking-tight mb-1">
              <Sparkles className="w-5 h-5 text-cyan-400" /> TRAVELMIND AI
            </div>
            <p className="text-xs text-gray-400 italic">Predict. Personalize. Plan.</p>
          </div>

          <div className="text-left sm:text-right">
            <span className="text-xs uppercase font-extrabold text-cyan-400 tracking-wider block">TAX INVOICE</span>
            <div className="text-2xl font-black text-white">{invoice.invoice_number}</div>
            <div className="text-xs text-gray-400 mt-1">
              Ref: <span className="text-gray-200 font-semibold">{invoice.booking_reference}</span> | Date: {invoice.created_at || '2026-08-14'}
            </div>
          </div>
        </div>

        {/* Customer & Booking Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Customer Details */}
          <div className="bg-gray-900/60 rounded-2xl p-5 border border-gray-800 space-y-3">
            <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
              <User className="w-4 h-4 text-cyan-400" /> Customer Details
            </h4>
            <div className="space-y-1.5 text-xs text-gray-300">
              <div><span className="text-gray-500 font-medium">Guest Name:</span> <strong className="text-white">{invoice.guest_name}</strong></div>
              <div><span className="text-gray-500 font-medium">Email:</span> <span className="text-gray-200">{invoice.guest_email}</span></div>
              <div><span className="text-gray-500 font-medium">Phone:</span> <span className="text-gray-200">{invoice.guest_phone}</span></div>
            </div>
          </div>

          {/* Booking Details */}
          <div className="bg-gray-900/60 rounded-2xl p-5 border border-gray-800 space-y-3">
            <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
              <Building className="w-4 h-4 text-indigo-400" /> Booking Details
            </h4>
            <div className="space-y-1.5 text-xs text-gray-300">
              <div><span className="text-gray-500 font-medium">Hotel:</span> <strong className="text-white">{invoice.hotel_name}</strong></div>
              <div><span className="text-gray-500 font-medium">Room Type:</span> <span className="text-gray-200">{invoice.room_type}</span></div>
              <div><span className="text-gray-500 font-medium">Stay Dates:</span> <span className="text-gray-200">{invoice.check_in} to {invoice.check_out}</span></div>
              <div><span className="text-gray-500 font-medium">Occupancy:</span> <span className="text-gray-200">{invoice.nights} Night(s) • {invoice.rooms} Room(s)</span></div>
            </div>
          </div>
        </div>

        {/* Price Breakdown Table */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" /> Price Breakdown
          </h4>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-900 border-b border-gray-800 text-gray-400 uppercase font-bold text-[10px]">
                  <th className="py-3 px-4">Item Description</th>
                  <th className="py-3 px-4 text-center">Nights / Rooms</th>
                  <th className="py-3 px-4 text-right">Rate</th>
                  <th className="py-3 px-4 text-right">Amount (₹)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 text-gray-200">
                <tr>
                  <td className="py-3.5 px-4 font-semibold text-white">
                    Room Charges — {invoice.room_type}
                    <div className="text-[10px] text-gray-400 font-normal">{invoice.hotel_name}</div>
                  </td>
                  <td className="py-3.5 px-4 text-center font-medium">{invoice.nights} Nights × {invoice.rooms} Room</td>
                  <td className="py-3.5 px-4 text-right">₹{invoice.room_price ? invoice.room_price.toLocaleString() : '3,500'}</td>
                  <td className="py-3.5 px-4 text-right font-bold text-white">₹{invoice.subtotal ? invoice.subtotal.toLocaleString() : '10,500'}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 text-gray-400" colSpan={3}>Subtotal</td>
                  <td className="py-2.5 px-4 text-right font-bold text-gray-200">₹{invoice.subtotal ? invoice.subtotal.toLocaleString() : '10,500'}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 text-gray-400" colSpan={3}>Tax (18% GST)</td>
                  <td className="py-2.5 px-4 text-right font-semibold text-gray-300">₹{invoice.tax ? invoice.tax.toLocaleString() : '1,890'}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 text-gray-400" colSpan={3}>Service Fee</td>
                  <td className="py-2.5 px-4 text-right font-semibold text-gray-300">₹{invoice.service_fee ? invoice.service_fee.toLocaleString() : '300'}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 text-emerald-400 font-medium" colSpan={3}>Discount Applied</td>
                  <td className="py-2.5 px-4 text-right font-bold text-emerald-400">-₹{invoice.discount ? invoice.discount.toLocaleString() : '500'}</td>
                </tr>
                <tr className="bg-cyan-500/10 font-extrabold text-sm border-t-2 border-cyan-500/30">
                  <td className="py-4 px-4 text-cyan-300 uppercase tracking-wider" colSpan={3}>TOTAL AMOUNT</td>
                  <td className="py-4 px-4 text-right text-cyan-400 text-lg">₹{invoice.total_amount ? invoice.total_amount.toLocaleString() : '12,190'}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Status Badges & Action Bar */}
        <div className="pt-4 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div>
              <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Payment Status</span>
              <span className={`inline-flex items-center gap-1 text-xs font-black px-3 py-1 rounded-full uppercase tracking-wider border ${
                isPaid
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : isFailed
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
              }`}>
                {isPaid ? <CheckCircle2 className="w-3.5 h-3.5" /> : isFailed ? <AlertCircle className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5" />}
                {invoice.payment_status || 'Pending'}
              </span>
            </div>

            <div>
              <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Booking Status</span>
              <span className="inline-flex items-center gap-1 text-xs font-bold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 uppercase">
                Confirmed
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {!isPaid && (
              <button
                onClick={() => handleDemoPayment(false)}
                disabled={paying}
                className="flex-1 sm:flex-initial px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-extrabold text-xs shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all transform hover:scale-105"
              >
                <CreditCard className="w-4 h-4" />
                {paying ? 'Processing Demo Payment...' : 'Pay Now - Demo'}
              </button>
            )}

            {!isPaid && (
              <button
                onClick={() => handleDemoPayment(true)}
                disabled={paying}
                title="Test Payment Failure state"
                className="px-3 py-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 font-bold text-[10px] border border-rose-500/20"
              >
                Simulate Failure
              </button>
            )}

            <button
              onClick={() => navigate('/trips')}
              className="px-4 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-bold text-xs border border-gray-700"
            >
              View Booking
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
