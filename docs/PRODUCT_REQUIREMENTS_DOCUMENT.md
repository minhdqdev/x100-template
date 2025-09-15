# Product Requirements Document (PRD)

## 1. Document Control
- **Project Code:** MSZ
- **Document Owner:** Product Team
- **Version:** v1.0 - Draft
- **Date:** 2025-08-25
- **Approvers:** Founder, CTO, Product Manager

---

## 2. Overview

### 2.1 Purpose

MasterZalo is a SaaS platform designed to transform personal Zalo accounts into unified CRM and marketing automation tools. The platform addresses the critical inefficiency Vietnamese businesses face managing customer relationships and marketing campaigns across multiple Zalo accounts, enabling them to scale their customer acquisition and communication processes.

### 2.2 Background & Context

Vietnamese businesses heavily rely on Zalo (75M+ users, 95% smartphone penetration) for customer communication, but lack proper tools to manage this at scale. Current solutions include:
- Manual management across multiple personal Zalo accounts (time-consuming, error-prone)
- Generic CRM tools (no Zalo integration, expensive for SMBs)
- Fragmented communication leading to missed opportunities and poor customer experience

Market trends support this initiative:
- COVID-19 accelerated SMB digital transformation
- Growing e-commerce and social selling in Vietnam
- Messaging-first customer communication preference
- Zalo's dominance as the primary business communication platform

### 2.3 Goals & Objectives

- **Primary Goal:** Enable Vietnamese SMBs to manage Zalo-based customer relationships efficiently
- **Business Goals:**
  - Achieve $50K MRR by end of year 1
  - Acquire 10,000 users within first 18 months
  - Establish 80%+ monthly user retention rate
- **User Goals:**
  - Reduce customer communication management time by 80%
  - Increase marketing campaign response rates by 15%+
  - Centralize customer data across multiple Zalo accounts

---

## 3. Scope

### 3.1 In-Scope

**Core CRM Features:**
- Unified dashboard for multiple Zalo account management
- Contact management and customer data centralization
- Chat history and conversation tracking
- Basic customer segmentation and tagging

**Marketing Automation:**
- Bulk messaging to friends, groups, and phone number lists
- Campaign creation and scheduling
- Group member messaging without joining groups
- Basic campaign analytics and reporting

**Database Features:**
- Access to curated library of 1K+ Vietnamese industry groups
- Group discovery and categorization
- Contact import/export functionality

### 3.2 Out-of-Scope

**Phase 1 Exclusions:**
- Advanced AI-powered customer insights
- Integration with other messaging platforms (WhatsApp, Facebook Messenger)
- Integration with Vietnamese e-commerce platforms
- Advanced analytics and business intelligence
- White-label solutions for agencies
- Mobile native applications (web-only initially)

---

## 4. Target Users

### 4.1 User Personas

**Primary Persona - SMB Owner "Minh"**
- Age: 30-45, Vietnamese business owner
- Industry: E-commerce, services, real estate
- Pain: Managing 3-5 Zalo accounts manually, missing customers
- Goal: Scale customer communication without hiring additional staff

**Secondary Persona - Marketing Manager "Linh"**
- Age: 25-35, manages marketing campaigns
- Focus: Lead generation and customer acquisition via Zalo
- Pain: Cannot efficiently reach target audiences in relevant groups
- Goal: Increase campaign effectiveness and ROI

**Tertiary Persona - Sales Team Lead "Duc"**
- Age: 28-40, manages sales team operations
- Challenge: Team coordination across multiple Zalo accounts
- Goal: Centralize customer data and improve team productivity

### 4.2 Use Cases / User Stories

- **As an SMB owner**, I want to manage multiple Zalo accounts from one dashboard, so that I can respond to customers faster and avoid missing messages
- **As a marketing manager**, I want to message group members directly without joining, so that I can reach potential customers efficiently
- **As a sales team lead**, I want to track all customer interactions in one place, so that my team can provide consistent service
- **As a business owner**, I want to run marketing campaigns to my contact lists, so that I can increase sales without manual outreach
- **As a marketer**, I want access to industry-specific Zalo groups, so that I can target the right audience for my campaigns

---

## 5. Requirements

### 5.1 Functional Requirements

**Account Management:**
- [FR-1] The system shall allow users to connect multiple personal Zalo accounts
- [FR-2] The system shall provide a unified dashboard showing all connected accounts
- [FR-3] The system shall sync chat history and contacts from connected accounts

**Customer Relationship Management:**
- [FR-4] Users can view all conversations from multiple accounts in one interface
- [FR-5] Users can tag and categorize contacts for segmentation
- [FR-6] The system shall store customer interaction history and notes
- [FR-7] Users can import and export contact lists in CSV format

**Marketing Automation:**
- [FR-8] Users can create and send bulk messages to contact lists
- [FR-9] Users can schedule marketing campaigns for future delivery
- [FR-10] Users can message any group member without joining the group
- [FR-11] The system shall provide campaign delivery reports and basic analytics

**Group Database (PRO Feature):**
- [FR-12] PRO users can access a curated database of 1K+ Vietnamese industry groups
- [FR-13] Users can search and filter groups by industry, location, and size
- [FR-14] The system shall regularly update the group database

### 5.2 Non-Functional Requirements (NFRs)

**Performance:**
- Dashboard loads within 3 seconds
- Message sending completes within 10 seconds for batches of 100
- Real-time chat updates with <2 second delay

**Security:**
- Secure storage of Zalo account credentials using encryption
- Compliance with Vietnamese data protection regulations
- User data isolation and access controls

**Scalability:**
- Support 10,000 concurrent users
- Handle 1M messages per month across all users
- 99.5% uptime availability

**Usability:**
- Vietnamese language interface
- Mobile-responsive web design
- Intuitive onboarding process (<10 minutes setup)

### 5.3 Assumptions & Dependencies

**Technical Assumptions:**
- Zalo public APIs remain stable and accessible
- No significant changes to Zalo's terms of service affecting business use
- Reliable internet connectivity for Vietnamese users

**Business Dependencies:**
- Successful integration with Zalo's official APIs
- Compliance approval for business use of personal Zalo accounts
- Development of Vietnamese language support and localization

---

## 6. User Experience & Design

**Key User Flows:**
1. **Account Setup Flow:** Connect Zalo accounts → Verify access → Import contacts → Dashboard setup
2. **Daily Management Flow:** Dashboard overview → Handle conversations → Update customer notes → Send follow-ups
3. **Campaign Creation Flow:** Create audience segment → Compose message → Schedule delivery → Monitor results
4. **Group Discovery Flow:** Search group database → Filter by criteria → Export member lists → Launch campaigns

**Design Principles:**
- Vietnamese-first interface and user experience
- Mobile-responsive for smartphone-heavy market
- Intuitive navigation minimizing learning curve
- Clear visual hierarchy for multi-account management

---

## 7. Success Metrics & KPIs

**User Adoption:**
- Monthly Active Users: 5,000+ by month 12
- Free-to-paid conversion rate: 25%+
- Average accounts per user: 3+

**User Engagement:**
- Daily messages sent per user: 10+
- Session duration: 15+ minutes average
- Monthly retention rate: 80%+

**Business Impact:**
- Campaign response rate improvement: 15%+ over manual methods
- Customer response time reduction: 60%+
- User-reported productivity increase: 80%+

**Revenue Metrics:**
- Monthly Recurring Revenue: $50K by month 12
- Customer Lifetime Value: $600+
- Customer Acquisition Cost: <$50

---

## 8. Risks & Mitigations

**Technical Risks:**
- **Zalo API changes** → Mitigation: Maintain close relationship with Zalo, build API abstraction layer
- **Rate limiting issues** → Mitigation: Implement intelligent queuing and throttling
- **Data synchronization problems** → Mitigation: Robust error handling and retry mechanisms

**Business Risks:**
- **Regulatory changes in Vietnam** → Mitigation: Legal review and compliance monitoring
- **Competition from Zalo official tools** → Mitigation: Focus on advanced features and superior UX
- **Market adoption slower than expected** → Mitigation: Aggressive content marketing and referral programs

**Operational Risks:**
- **Support in Vietnamese required** → Mitigation: Hire local support team
- **Payment processing in Vietnam** → Mitigation: Partner with local payment providers

---

## 9. Release Plan

### MVP Scope (Phase 1 - Q1)
- Multi-account Zalo dashboard
- Basic contact management (miniCRM)
- Group member messaging capability
- Simple campaign sending to contact lists
- Basic reporting and analytics

### Phase 2 (Q2-Q3)
- Industry group database (PRO feature)
- Advanced customer segmentation
- Campaign scheduling and automation
- Enhanced reporting and analytics
- Mobile optimization improvements

### Future Iterations (Q4+)
- AI-powered customer insights
- Integration with Vietnamese e-commerce platforms
- Advanced workflow automation
- WhatsApp and Facebook Messenger support
- Agency and enterprise features

### Timeline
- **MVP Development:** 3 months
- **Beta Testing:** 1 month
- **Market Launch:** Month 5
- **Feature Enhancement:** Ongoing

---

## 10. Appendix

**Glossary of Terms:**
- **Zalo:** Vietnam's dominant messaging platform (similar to WhatsApp)
- **SMB:** Small to Medium Business (10-200 employees)
- **Group Member Messaging:** Ability to message any member of a Zalo group without joining
- **TAM/SAM/SOM:** Total/Serviceable/Serviceable Obtainable Market

**Supporting Research:**
- Vietnam messaging app usage statistics
- SMB digital transformation trends in Southeast Asia  
- Competitive analysis of CRM tools in Vietnamese market
- Zalo API documentation and capabilities assessment