# Product Requirements Document (PRD)

## 1. Document Control

- **Document Owner:** Product Manager / Technical Lead
- **Version:** v1.0
- **Date:** 2025-08-25
- **Approvers:** Product Owner, Engineering Lead, Business Development

---

## 2. Overview

### 2.1 Purpose

MasterZalo is a comprehensive SaaS platform that transforms personal Zalo accounts into a unified CRM and marketing automation tool. The platform addresses the critical pain point of Vietnamese businesses struggling to efficiently manage customer relationships and marketing campaigns across multiple Zalo accounts.

### 2.2 Background & Context

The Vietnamese market presents a unique opportunity with Zalo's dominance (75M+ users, 95% smartphone penetration). Current solutions are either generic CRM tools not integrated with Zalo or manual processes that are time-consuming and unscalable. Small to medium Vietnamese businesses lose potential customers due to slow response times and miss marketing opportunities due to fragmented account management.

### 2.3 Goals & Objectives

- **Primary Goal:** Enable Vietnamese SMBs to achieve 80% time savings on customer communication management
- **User Acquisition:** Reach 10,000 active users within 12 months
- **Revenue Target:** Generate $50K MRR by end of year 1
- **Market Position:** Establish as the standard platform for Zalo-based business communication in Vietnam
- **User Engagement:** Achieve >15% response rate on marketing campaigns

---

## 3. Scope

### 3.1 In-Scope

- **Multi-account Management:** Unified dashboard for managing multiple Zalo accounts simultaneously
- **Direct Messaging:** Capability to message group members without joining groups
- **Marketing Automation:** Automated campaign management for friends, groups, and phone number lists
- **Customer Management:** MiniCRM features for lead tracking and customer relationship management
- **Group Database:** Access to 1K+ curated Zalo groups across Vietnamese industries (PRO feature)
- **Real-time Chat:** Live chat management with WebSocket technology
- **Campaign Analytics:** Basic performance tracking and reporting
- **Vietnamese Localization:** Full Vietnamese language support and local market optimization

### 3.2 Out-of-Scope

- **Phase 1:** Integration with other messaging platforms (Facebook Messenger, WhatsApp)
- **Advanced AI:** Complex AI-powered customer insights (planned for Phase 2)
- **E-commerce Integration:** Direct integration with Vietnamese e-commerce platforms (planned for Phase 3)
- **Mobile App:** Native mobile applications (web-first approach)
- **International Markets:** Markets outside Vietnam and Southeast Asia

---

## 4. Target Users

### 4.1 User Personas

**Primary Persona - Minh (Small Business Owner)**
- Age: 35, owns e-commerce business selling fashion accessories
- Uses 3-4 Zalo accounts for different product lines
- Spends 4+ hours daily managing customer chats manually
- Needs: Centralized management, automated responses, lead tracking

**Secondary Persona - Linh (Digital Marketing Specialist)**
- Age: 28, works at marketing agency serving Vietnamese SMBs
- Manages Zalo marketing for 10+ clients
- Struggles with group outreach and campaign tracking
- Needs: Bulk messaging, performance analytics, client reporting

**Tertiary Persona - Duc (Sales Team Lead)**
- Age: 42, manages 5-person sales team for real estate company
- Each team member has 2-3 Zalo accounts for different areas
- Needs unified customer database and team collaboration features

### 4.2 Use Cases / User Stories

- As a business owner, I want to manage all my Zalo accounts from one dashboard, so that I can respond faster to customers
- As a marketer, I want to send messages to group members without joining groups, so that I can expand my reach efficiently
- As a sales manager, I want to track leads across multiple team members' Zalo accounts, so that I can optimize our sales process
- As a small business owner, I want to automate follow-up messages to customers, so that I can focus on other business activities
- As a marketing agency, I want to access industry-specific group databases, so that I can target the right audience for my clients

---

## 5. Requirements

### 5.1 Functional Requirements

- **[FR-1]** The system shall allow users to connect and manage multiple Zalo accounts from a unified dashboard
- **[FR-2]** The system shall enable direct messaging to group members without requiring group membership
- **[FR-3]** The system shall provide campaign creation and scheduling for bulk messaging
- **[FR-4]** The system shall maintain a customer database with contact information, conversation history, and lead status
- **[FR-5]** The system shall provide access to curated Zalo groups database (1K+ groups across industries)
- **[FR-6]** The system shall support real-time chat management with live message synchronization
- **[FR-7]** The system shall generate campaign performance reports and analytics
- **[FR-8]** The system shall implement tiered access controls (Free, PRO, Enterprise plans)
- **[FR-9]** The system shall support Vietnamese language interface and content
- **[FR-10]** The system shall provide contact import/export functionality

### 5.2 Non-Functional Requirements (NFRs)

- **Performance:** Dashboard loads < 3 seconds, message sending < 1 second response time
- **Scalability:** Support 10,000 concurrent users with 100+ Zalo accounts each
- **Availability:** 99.5% uptime with scheduled maintenance windows
- **Security:** End-to-end encryption for messages, secure Zalo API token storage
- **Compliance:** Adhere to Vietnam data protection regulations and Zalo API terms
- **Reliability:** Message delivery rate > 95%, data backup every 4 hours
- **Usability:** Intuitive interface requiring < 30 minutes onboarding time

### 5.3 Assumptions & Dependencies

- **Assumes:** Zalo API remains stable and accessible for third-party integrations
- **Assumes:** Target users have basic technical literacy for web applications
- **Dependent on:** Zalo API rate limits and policy compliance
- **Dependent on:** Vietnamese internet infrastructure for real-time features
- **Dependent on:** Payment gateway integration for subscription management

---

## 6. User Experience & Design

### Key User Flows

1. **Account Connection Flow:**
   - User registration → Zalo account authentication → Dashboard access
   - Target completion time: < 5 minutes

2. **Campaign Creation Flow:**
   - Contact selection → Message composition → Schedule setting → Campaign launch
   - Support for templates and personalization variables

3. **Group Discovery Flow:**
   - Industry selection → Group browsing → Contact extraction → Campaign targeting
   - Available only for PRO subscribers

4. **Customer Management Flow:**
   - Contact creation → Conversation tracking → Lead status updates → Follow-up scheduling

### Design Requirements

- **Responsive Design:** Optimized for desktop (primary) and tablet usage
- **Vietnamese UI:** All interface elements translated and culturally appropriate
- **Dashboard Layout:** Multi-pane interface with chat, contacts, and analytics sections
- **Color Scheme:** Professional blues and greens aligned with Vietnamese business preferences

---

## 7. Success Metrics & KPIs

### Primary Metrics
- **Monthly Recurring Revenue (MRR):** Target $50K by month 12
- **User Acquisition:** 100 users in month 1, 10,000 users by month 12
- **Free to Paid Conversion:** >25% conversion rate within 30 days
- **Monthly Active Users:** >80% retention rate
- **Account Adoption:** Average 3+ Zalo accounts connected per user

### Engagement Metrics
- **Daily Message Volume:** >10 messages sent per user per day
- **Campaign Performance:** >15% response rate on marketing campaigns
- **Time to Value:** <7 days from signup to first successful campaign
- **Feature Adoption:** >60% users utilizing automation features
- **Support Tickets:** <5% of users requiring support monthly

### Business Metrics
- **Customer Acquisition Cost (CAC):** Target $25-50 per SMB customer
- **Lifetime Value (LTV):** $600+ (average 2-year subscription)
- **Net Promoter Score (NPS):** >40 from Vietnamese SMB users
- **Churn Rate:** <10% monthly churn for paid subscribers

---

## 8. Risks & Mitigations

### Technical Risks
- **Risk:** Zalo API policy changes or rate limiting → **Mitigation:** Diversify API usage, maintain compliance buffer, develop API monitoring
- **Risk:** System overload during peak usage → **Mitigation:** Auto-scaling infrastructure, performance monitoring, load testing

### Business Risks
- **Risk:** Competitive response from established players → **Mitigation:** First-mover advantage, deep market knowledge, patent key innovations
- **Risk:** Regulatory changes in Vietnam → **Mitigation:** Legal compliance review, government relations, privacy-by-design approach

### Market Risks
- **Risk:** Slower than expected adoption → **Mitigation:** Aggressive referral programs, partnership channels, product-market fit iteration
- **Risk:** Zalo platform popularity decline → **Mitigation:** Multi-platform strategy roadmap, monitoring alternative channels

---

## 9. Release Plan

### MVP Scope (Month 1-3)
- Multi-account Zalo dashboard
- Basic contact management (miniCRM)
- Group member messaging functionality  
- Campaign creation and scheduling
- User authentication and subscription management

### Phase 2 Features (Month 4-6)
- Advanced analytics and reporting
- Group database access (1K+ curated groups)
- Template library and personalization
- Team collaboration features
- Mobile-responsive optimization

### Phase 3 Enhancements (Month 7-12)
- AI-powered customer insights
- Advanced automation workflows
- Integration APIs for third-party tools
- Enterprise features and white-labeling
- Performance optimization and scaling

### Timeline
- **Month 1:** Core development completion, alpha testing
- **Month 2:** Beta release to 50 selected users, iteration based on feedback  
- **Month 3:** Public launch with freemium model
- **Month 6:** PRO features rollout, partnership channels activation
- **Month 12:** Enterprise tier launch, expansion planning

---

## 10. Appendix

### Glossary of Terms
- **Zalo:** Vietnam's dominant messaging platform (similar to WhatsApp)
- **SMB:** Small and Medium Business (10-200 employees)
- **MiniCRM:** Lightweight customer relationship management features
- **Group Member Messaging:** Ability to contact group members without joining the group

### Supporting Documentation
- Market research on Vietnamese SMB messaging behavior
- Competitive analysis of existing CRM solutions
- Zalo API documentation and integration guidelines
- User interview transcripts and persona research
- Technical architecture and system design documents